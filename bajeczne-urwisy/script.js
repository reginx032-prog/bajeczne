/* =========================================================
   Bajeczne Urwisy: interaktywność strony
   ========================================================= */
(function () {
  "use strict";

  document.documentElement.classList.add("js-ready");
  var motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  var motionPaused = motionQuery.matches;
  var updateMotionPreference = function () {
    document.documentElement.classList.toggle("motion-paused", motionPaused);
    if (typeof rsRestartTimer === "function") rsRestartTimer();
  };
  if (motionQuery.addEventListener) {
    motionQuery.addEventListener("change", function (event) {
      motionPaused = event.matches;
      updateMotionPreference();
    });
  }
  updateMotionPreference();

  var updatePageVisibility = function () {
    document.documentElement.classList.toggle("page-hidden", !!document.hidden);
    if (typeof rsRestartTimer === "function") rsRestartTimer();
  };
  document.addEventListener("visibilitychange", updatePageVisibility);
  updatePageVisibility();

  /* ---- Rok w stopce ---- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---- Nagłówek reagujący na kierunek przewijania ---- */
  var header = document.querySelector(".site-header");
  var nav = document.getElementById("nav");
  var headerOffset = 108;
  var headerTravel = 0;
  var headerScrollY = function () {
    var limit = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    return Math.max(0, Math.min(window.scrollY || 0, limit));
  };
  var lastHeaderY = headerScrollY();
  var showHeader = function () {
    if (header) header.classList.remove("is-hidden");
    headerTravel = 0;
    lastHeaderY = headerScrollY();
  };
  var syncHeaderOffset = function () {
    headerOffset = header ? Math.ceil(header.getBoundingClientRect().height) + 20 : 20;
    document.documentElement.style.setProperty("--anchor-offset", headerOffset + "px");
    showHeader();
  };
  syncHeaderOffset();
  window.addEventListener("resize", syncHeaderOffset, { passive: true });
  if (header) header.addEventListener("focusin", showHeader);
  if (header && "ResizeObserver" in window) {
    new ResizeObserver(syncHeaderOffset).observe(header);
  }
  var headerTicking = false;
  var onScroll = function () {
    if (!header || headerTicking) return;
    headerTicking = true;
    requestAnimationFrame(function () {
      var currentY = headerScrollY();
      var delta = currentY - lastHeaderY;
      var keepVisible = currentY <= headerOffset - 20 || navigationTarget ||
        header.contains(document.activeElement) || header.querySelector(".sub-open") ||
        (nav && nav.classList.contains("open"));
      header.classList.toggle("scrolled", currentY > 12);
      if (keepVisible) {
        header.classList.remove("is-hidden");
        headerTravel = 0;
      } else if (delta) {
        headerTravel = headerTravel * delta > 0 ? headerTravel + delta : delta;
        if (Math.abs(headerTravel) >= 8) {
          header.classList.toggle("is-hidden", headerTravel > 0);
          headerTravel = 0;
        }
      }
      lastHeaderY = currentY;
      headerTicking = false;
    });
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- Rozwijane pozycje nawigacji ---- */
  var closeSubmenus = function (except) {
    document.querySelectorAll(".nav-links .has-sub.sub-open").forEach(function (item) {
      if (except && item === except) return;
      item.classList.remove("sub-open");
      var itemToggle = item.querySelector(".nav-sub-toggle");
      if (itemToggle) itemToggle.setAttribute("aria-expanded", "false");
    });
  };
  var desktopNav = window.matchMedia("(min-width: 1281px)");
  document.querySelectorAll(".nav-sub-toggle").forEach(function (button) {
    var item = button.closest(".has-sub");
    if (!item) return;
    var setOpen = function (open) {
      closeSubmenus(open ? item : null);
      item.classList.toggle("sub-open", open);
      button.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) showHeader();
    };
    button.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      setOpen(!item.classList.contains("sub-open"));
    });
    button.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowDown") return;
      event.preventDefault();
      setOpen(true);
      var first = item.querySelector(".nav-sub a");
      if (first) first.focus();
    });
    item.addEventListener("mouseenter", function () {
      if (desktopNav.matches && window.matchMedia("(hover: hover)").matches) setOpen(true);
    });
    item.addEventListener("mouseleave", function () {
      if (desktopNav.matches && !item.contains(document.activeElement)) setOpen(false);
    });
    item.addEventListener("focusout", function (event) {
      if (!item.contains(event.relatedTarget)) setOpen(false);
    });
  });

  /* ---- Menu mobilne ---- */
  var toggle = document.getElementById("navToggle");
  var closeMobileMenu = function (restoreFocus) {
    if (!nav || !toggle) return;
    var wasOpen = nav.classList.contains("open");
    nav.classList.remove("open");
    closeSubmenus(null);
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Otwórz menu");
    if (wasOpen && restoreFocus) toggle.focus();
  };
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Zamknij menu" : "Otwórz menu");
      if (open) showHeader();
      if (!open) closeSubmenus(null);
    });
    // Zamknij menu po kliknięciu w link
    nav.querySelectorAll(".nav-links a").forEach(function (a) {
      a.addEventListener("click", function () {
        closeMobileMenu(false);
      });
    });
    nav.addEventListener("focusout", function (event) {
      if (!nav.contains(event.relatedTarget)) closeMobileMenu(false);
    });
  }
  document.addEventListener("click", function (event) {
    if (nav && !nav.contains(event.target)) closeMobileMenu(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape") return;
    var activeSub = document.activeElement && document.activeElement.closest(".has-sub.sub-open");
    if (nav && nav.classList.contains("open")) closeMobileMenu(true);
    else {
      closeSubmenus(null);
      if (activeSub) activeSub.querySelector(".nav-sub-toggle").focus();
    }
  });
  if (desktopNav.addEventListener) {
    desktopNav.addEventListener("change", function () { closeMobileMenu(false); });
  }

  /* ---- Jedno zaznaczenie w menu, także podczas długiego przejścia ---- */
  var fragmentTarget = function (hash) {
    if (!hash || hash.charAt(0) !== "#" || hash.length < 2) return null;
    try { return document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch (error) { return null; }
  };
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
  var navSections = navLinks.map(function (link) {
    var hash = link.getAttribute("href");
    var target = fragmentTarget(hash);
    return target ? { hash: hash, target: target } : null;
  }).filter(Boolean);
  var navigationTarget = null;
  var navigationTimer = null;
  var navTicking = false;
  var updateActiveNavigation = function () {
    if (!navSections.length) return;
    var activeHash = navigationTarget;
    if (!activeHash) {
      var closestTop = -Infinity;
      activeHash = navSections[0].hash;
      navSections.forEach(function (section) {
        var top = section.target.getBoundingClientRect().top;
        if (top <= headerOffset + 2 && top > closestTop) {
          closestTop = top;
          activeHash = section.hash;
        }
      });
    }
    navLinks.forEach(function (link) {
      link.classList.toggle("active", link.getAttribute("href") === activeHash);
    });
  };
  var finishNavigation = function () {
    window.clearTimeout(navigationTimer);
    navigationTarget = null;
    updateActiveNavigation();
  };
  var waitForScrollEnd = function () {
    window.clearTimeout(navigationTimer);
    navigationTimer = window.setTimeout(finishNavigation, 180);
  };
  if (navSections.length) {
    window.addEventListener("scroll", function () {
      if (navigationTarget) waitForScrollEnd();
      if (navTicking) return;
      navTicking = true;
      requestAnimationFrame(function () {
        updateActiveNavigation();
        navTicking = false;
      });
    }, { passive: true });
    // Ręczne przewijanie i historia przeglądarki oddają sterowanie użytkownikowi.
    window.addEventListener("wheel", finishNavigation, { passive: true });
    window.addEventListener("touchstart", finishNavigation, { passive: true });
    window.addEventListener("popstate", finishNavigation);
    window.addEventListener("hashchange", finishNavigation);
    window.addEventListener("resize", finishNavigation, { passive: true });
    document.addEventListener("keydown", function (event) {
      if (["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End", " "].indexOf(event.key) !== -1) finishNavigation();
    });
    updateActiveNavigation();
  }

  /* ---- Płynne przewijanie do kotwic ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (e.defaultPrevented || e.button > 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      var id = link.getAttribute("href");
      var target = fragmentTarget(id);
      if (!target) return;
      e.preventDefault();
      closeMobileMenu(false);
      syncHeaderOffset();
      navigationTarget = navSections.some(function (section) { return section.hash === id; }) ? id : null;
      updateActiveNavigation();
      waitForScrollEnd();
      if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      var top = id === "#top" ? 0 : Math.max(0, target.getBoundingClientRect().top + window.scrollY - headerOffset);
      if (window.location.hash !== id) {
        try { window.history.pushState(null, "", id); }
        catch (error) { window.location.hash = id; return; }
      }
      window.scrollTo({ top: top, behavior: motionQuery.matches || motionPaused ? "auto" : "smooth" });
    });
  });

  /* ---- Płynące rzędy zdjęć w hero ---- */
  var heroWalls = document.querySelectorAll(".hero-wall");
  if (heroWalls.length) {
    heroWalls.forEach(function (heroWall) {
      heroWall.querySelectorAll(".hw-track").forEach(function (track) {
      Array.prototype.slice.call(track.children).forEach(function (item) {
        var clone = item.cloneNode(true);
        clone.setAttribute("aria-hidden", "true");
        track.appendChild(clone);
      });
    });
    });

    var reduceMotion = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduceMotion) {
      heroWalls.forEach(function (heroWall) { heroWall.classList.add("is-paused"); });
    } else if ("IntersectionObserver" in window) {
      var heroMotion = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            entry.target.classList.toggle("is-paused", !entry.isIntersecting);
          });
        },
        { threshold: 0.05, rootMargin: "120px 0px" }
      );
      heroWalls.forEach(function (heroWall) { heroMotion.observe(heroWall); });
    }
  }

  /* ---- Efekt łączenia z lewej i prawej strony ---- */
  var mergeItems = Array.prototype.slice.call(
    document.querySelectorAll(".scroll-from-left, .scroll-from-right")
  );
  var mergeReducedMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mergeDistance = 1240;
  var updateMergeDistance = function () {
    var vw = window.innerWidth || document.documentElement.clientWidth || 1200;
    /* pełna szerokość okna: element startuje całkowicie poza ekranem */
    mergeDistance = vw + 40;
  };
  var easeMerge = function (value) {
    return 1 - Math.pow(1 - value, 3);
  };
  var setMergeProgress = function (el, ratio) {
    var progress = Math.max(0, Math.min(1, ratio));
    if (el._mergeProgress === progress && el._mergeDistance === mergeDistance) return;
    el._mergeProgress = progress;
    el._mergeDistance = mergeDistance;
    var eased = easeMerge(progress);
    var direction = el.classList.contains("scroll-from-left") ? -1 : 1;
    var x = direction * mergeDistance * (1 - eased);
    var scale = 0.94 + (0.06 * eased);
    var opacity = 0.16 + (0.84 * eased);

    el.style.transform = "translate3d(" + x.toFixed(1) + "px, 0, 0) scale(" + scale.toFixed(4) + ")";
    el.style.opacity = opacity.toFixed(3);
  };
  var getMergeAnchor = function (el) {
    return el.closest(".scroll-merge, .gallery-intro, .contact-grid, .steps, .trust-wrap, .breeds-layout, .about-grid") || el;
  };
  var getMergeProgress = function (el) {
    if (el.contains(document.activeElement)) return 1;
    var anchor = el._mergeAnchor || el;
    var rect = anchor.getBoundingClientRect();
    var viewportH = window.innerHeight || document.documentElement.clientHeight || 800;
    var start = viewportH * 0.92;
    var end = viewportH * 0.36;
    return Math.max(0, Math.min(1, (start - rect.top) / (start - end)));
  };

  updateMergeDistance();

  if (mergeItems.length && !mergeReducedMotion) {
    var mergeTicking = false;
    var updateMergeItems = function () {
      mergeTicking = false;
      if (motionPaused || motionQuery.matches || window.innerWidth <= 760) return;
      // Read geometry first, then write styles to avoid repeated layout work.
      var progress = mergeItems.map(getMergeProgress);
      mergeItems.forEach(function (el, index) {
        setMergeProgress(el, progress[index]);
      });
    };
    var requestMergeUpdate = function () {
      if (mergeTicking || document.hidden || motionPaused || motionQuery.matches || window.innerWidth <= 760) return;
      mergeTicking = true;
      requestAnimationFrame(updateMergeItems);
    };

    mergeItems.forEach(function (el) {
      el._mergeAnchor = getMergeAnchor(el);
      el.classList.add("scroll-merge-live");
      setMergeProgress(el, 0);
    });
    requestMergeUpdate();
    window.addEventListener("scroll", requestMergeUpdate, { passive: true });
    window.addEventListener("resize", function () {
      updateMergeDistance();
      requestMergeUpdate();
    }, { passive: true });
    window.addEventListener("load", requestMergeUpdate, { once: true });
    document.addEventListener("focusin", requestMergeUpdate);
  } else {
    mergeItems.forEach(function (el) {
      el.classList.add("in");
      el.style.opacity = "";
      el.style.transform = "";
    });
  }

  /* ---- Animacje wejścia (scroll reveal) ---- */
  var reveals = document.querySelectorAll(".reveal");
  reveals.forEach(function (el) { el.classList.add("reveal-ready"); });
  var markVisibleReveals = function () {
    var viewportH = window.innerHeight || document.documentElement.clientHeight;
    var viewportW = window.innerWidth || document.documentElement.clientWidth;
    var visible = Array.prototype.filter.call(reveals, function (el) {
      if (el.classList.contains("in")) return false;
      var rect = el.getBoundingClientRect();
      return (
        rect.bottom > -90 &&
        rect.top < viewportH + 90 &&
        rect.right > -160 &&
        rect.left < viewportW + 160
      );
    });
    visible.forEach(function (el) { el.classList.add("in"); });
  };

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.04, rootMargin: "18% 28% 18% 28%" }
    );
    reveals.forEach(function (el) { io.observe(el); });
    requestAnimationFrame(markVisibleReveals);
    window.addEventListener("load", markVisibleReveals, { once: true });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- Szczenięta: przewijanie kart przyciskami ---- */
  var puppyTrack = document.querySelector("[data-puppy-track]");
  var puppyPrev = document.querySelector("[data-puppy-prev]");
  var puppyNext = document.querySelector("[data-puppy-next]");
  if (puppyTrack && puppyPrev && puppyNext) {
    var puppyReducedMotion = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var puppyUpdateScheduled = false;

    var puppyStep = function () {
      var card = puppyTrack.querySelector(".puppy");
      if (!card) return Math.max(260, puppyTrack.clientWidth * .82);
      var gap = parseFloat(getComputedStyle(puppyTrack).columnGap) ||
        parseFloat(getComputedStyle(puppyTrack).gap) || 24;
      return card.getBoundingClientRect().width + gap;
    };

    var puppyMaxScroll = function () {
      return Math.max(0, puppyTrack.scrollWidth - puppyTrack.clientWidth);
    };

    var puppyUpdateButtons = function () {
      var max = puppyMaxScroll();
      puppyPrev.disabled = puppyTrack.scrollLeft <= 4;
      puppyNext.disabled = puppyTrack.scrollLeft >= max - 4;
    };

    var puppyScheduleUpdate = function () {
      if (puppyUpdateScheduled) return;
      puppyUpdateScheduled = true;
      requestAnimationFrame(function () {
        puppyUpdateScheduled = false;
        puppyUpdateButtons();
      });
    };

    var puppyMove = function (direction) {
      var max = puppyMaxScroll();
      var target = puppyTrack.scrollLeft + (puppyStep() * direction);
      puppyTrack.scrollTo({
        left: Math.max(0, Math.min(max, target)),
        behavior: puppyReducedMotion ? "auto" : "smooth"
      });
    };

    puppyPrev.addEventListener("click", function () { puppyMove(-1); });
    puppyNext.addEventListener("click", function () { puppyMove(1); });
    puppyTrack.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        puppyMove(-1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        puppyMove(1);
      }
    });
    puppyTrack.addEventListener("scroll", puppyScheduleUpdate, { passive: true });
    window.addEventListener("resize", puppyScheduleUpdate, { passive: true });
    window.addEventListener("load", puppyUpdateButtons, { once: true });
    puppyUpdateButtons();
  }

  /* ---- Opinie: karuzela z timerem, strzałkami i przeciąganiem ---- */
  var reviewsCarousel = document.querySelector("[data-reviews-carousel]");
  if (reviewsCarousel) {
    var rsStrip = reviewsCarousel.querySelector("[data-reviews-strip]");
    var rsTrack = reviewsCarousel.querySelector("[data-rs-track]");
    var rsPrev = reviewsCarousel.querySelector("[data-rs-prev]");
    var rsNext = reviewsCarousel.querySelector("[data-rs-next]");

    var rsStep = function () {
      var card = rsTrack ? rsTrack.querySelector(".rs-card") : null;
      if (!card) return 360;
      var gap = parseFloat(getComputedStyle(rsTrack).columnGap) || 20;
      return card.getBoundingClientRect().width + gap;
    };
    var rsMaxScroll = function () {
      return Math.max(0, rsStrip.scrollWidth - rsStrip.clientWidth);
    };
    var rsGoTo = function (left) {
      rsStrip.scrollTo({ left: left, behavior: motionQuery.matches || motionPaused ? "auto" : "smooth" });
    };
    var rsMove = function (direction) {
      var step = rsStep();
      var max = rsMaxScroll();
      var target = (Math.round(rsStrip.scrollLeft / step) + direction) * step;
      if (direction > 0 && rsStrip.scrollLeft >= max - 4) target = 0;
      else if (direction < 0 && rsStrip.scrollLeft <= 4) target = max;
      rsGoTo(Math.min(max, Math.max(0, target)));
    };

    /* timer: kolejna karta co 5 sekund, gdy nikt nie korzysta */
    var rsHover = false;
    var rsFocus = false;
    var rsOffscreen = false;
    var rsPointerActive = false;
    var rsTimer = null;
    var rsRestartTimer = function () {
      if (rsTimer) window.clearInterval(rsTimer);
      rsTimer = null;
      if (motionPaused || motionQuery.matches || rsOffscreen || document.hidden) return;
      rsTimer = window.setInterval(function () {
        if (motionPaused || motionQuery.matches || rsHover || rsFocus || rsOffscreen || rsPointerActive || document.hidden) return;
        rsMove(1);
      }, 5000);
    };

    reviewsCarousel.addEventListener("mouseenter", function () { rsHover = true; });
    reviewsCarousel.addEventListener("mouseleave", function () { rsHover = false; });
    reviewsCarousel.addEventListener("focusin", function () { rsFocus = true; });
    reviewsCarousel.addEventListener("focusout", function (event) {
      rsFocus = reviewsCarousel.contains(event.relatedTarget);
    });
    if ("IntersectionObserver" in window) {
      var rsObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            var offscreen = !entry.isIntersecting;
            if (rsOffscreen !== offscreen) {
              rsOffscreen = offscreen;
              rsRestartTimer();
            }
          });
        },
        { threshold: 0.05, rootMargin: "80px 0px" }
      );
      rsObserver.observe(reviewsCarousel);
    }

    if (rsPrev) {
      rsPrev.addEventListener("click", function () {
        rsMove(-1);
        rsRestartTimer();
      });
    }
    if (rsNext) {
      rsNext.addEventListener("click", function () {
        rsMove(1);
        rsRestartTimer();
      });
    }

    rsStrip.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        rsMove(-1);
        rsRestartTimer();
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        rsMove(1);
        rsRestartTimer();
      }
    });

    /* przeciąganie myszką (dotyk przewija natywnie) */
    var rsDrag = null;
    var rsSuppressClick = false;
    rsStrip.addEventListener("pointerdown", function (event) {
      if (event.pointerType !== "mouse" || event.button !== 0) return;
      rsDrag = { startX: event.clientX, startLeft: rsStrip.scrollLeft, moved: false };
      rsPointerActive = true;
      rsStrip.classList.add("is-dragging");
    });
    window.addEventListener("pointermove", function (event) {
      if (!rsDrag) return;
      var delta = event.clientX - rsDrag.startX;
      if (Math.abs(delta) > 5) rsDrag.moved = true;
      rsStrip.scrollLeft = rsDrag.startLeft - delta;
    });
    var rsEndDrag = function () {
      if (!rsDrag) return;
      var moved = rsDrag.moved;
      rsDrag = null;
      rsPointerActive = false;
      rsStrip.classList.remove("is-dragging");
      if (moved) {
        rsSuppressClick = true;
        window.setTimeout(function () { rsSuppressClick = false; }, 80);
        var step = rsStep();
        rsGoTo(Math.min(rsMaxScroll(), Math.max(0, Math.round(rsStrip.scrollLeft / step) * step)));
      }
      rsRestartTimer();
    };
    window.addEventListener("pointerup", rsEndDrag);
    window.addEventListener("pointercancel", rsEndDrag);
    rsStrip.addEventListener("click", function (event) {
      if (rsSuppressClick) {
        rsSuppressClick = false;
        event.preventDefault();
        event.stopPropagation();
      }
    }, true);

    /* oznacz karty z przyciętym cytatem ("Przeczytaj całość") */
    var rsMarkClamped = function () {
      var measurements = Array.prototype.map.call(rsTrack.querySelectorAll(".rs-card"), function (card) {
        var quote = card.querySelector(".rs-quote");
        return { card: card, clamped: !!quote && quote.scrollHeight > quote.clientHeight + 2 };
      });
      measurements.forEach(function (measurement) {
        measurement.card.classList.toggle("is-clamped", measurement.clamped);
      });
    };
    rsMarkClamped();
    window.addEventListener("load", rsMarkClamped, { once: true });
    window.addEventListener("resize", rsMarkClamped, { passive: true });

    rsRestartTimer();
  }

  /* ---- Galeria: filtry ras ---- */
  var mosaic = document.querySelector("[data-gallery-mosaic]");
  if (mosaic) {
    var mosaicTiles = Array.prototype.slice.call(mosaic.querySelectorAll(".mosaic-tile"));
    var galleryFilters = Array.prototype.slice.call(document.querySelectorAll(".gallery-filter"));

    galleryFilters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var value = btn.getAttribute("data-filter");

        galleryFilters.forEach(function (other) {
          var active = other === btn;
          other.classList.toggle("is-active", active);
          other.setAttribute("aria-pressed", active ? "true" : "false");
        });

        mosaicTiles.forEach(function (tile) {
          var visible = value === "all" || tile.getAttribute("data-breed") === value;
          tile.classList.toggle("is-hidden", !visible);
        });
      });
    });
  }

  /* ---- Lightbox galerii ---- */
  var lightbox = document.getElementById("lightbox");
  var lightboxClose = document.getElementById("lightboxClose");
  if (lightbox) {
    var lightboxTrigger = null;
    var previousOverflow = "";
    var backgroundState = [];
    var showLightbox = function (trigger, label) {
      if (lightbox.classList.contains("open")) return;
      lightboxTrigger = trigger || document.activeElement;
      previousOverflow = document.body.style.overflow;
      backgroundState = Array.prototype.slice.call(document.body.children)
        .filter(function (el) { return el !== lightbox && !/^(SCRIPT|STYLE|LINK)$/.test(el.tagName); })
        .map(function (el) { return { element: el, inert: el.inert }; });
      backgroundState.forEach(function (state) { state.element.inert = true; });
      lightbox.setAttribute("aria-label", label);
      lightbox.classList.add("open");
      document.body.style.overflow = "hidden";
      if (lightboxClose) lightboxClose.focus({ preventScroll: true });
    };
    document.querySelectorAll(".mosaic-tile").forEach(function (item) {
      item.addEventListener("click", function () {
        var img = item.querySelector("img");
        var inner = lightbox.querySelector(".lightbox-inner");
        inner.removeAttribute("tabindex");
        if (img) {
          var figure = document.createElement("figure");
          var preview = document.createElement("img");

          preview.src = img.src;
          preview.alt = img.alt || "";
          preview.decoding = "async";

          figure.className = "lightbox-figure";
          figure.appendChild(preview);
          inner.replaceChildren(figure);
        }
        showLightbox(item, "Podgląd zdjęcia");
      });
    });
    /* pełna opinia w lightboxie */
    var openReview = function (card) {
      var inner = lightbox.querySelector(".lightbox-inner");
      inner.setAttribute("tabindex", "0");
      var wrap = document.createElement("div");
      wrap.className = "lightbox-review";

      var photoImg = card.querySelector(".rs-photo img");
      if (photoImg) {
        var fig = document.createElement("figure");
        var img = document.createElement("img");
        img.src = photoImg.src;
        img.alt = photoImg.alt || "";
        fig.appendChild(img);
        wrap.appendChild(fig);
      }

      var body = document.createElement("div");
      body.className = "lr-body";

      var stars = document.createElement("div");
      stars.className = "lr-stars";
      stars.setAttribute("aria-label", "5 na 5 gwiazdek");
      stars.textContent = "★★★★★";

      var quoteSource = card.querySelector(".rs-quote");
      var quote = document.createElement("p");
      quote.className = "lr-quote";
      quote.textContent = quoteSource ? quoteSource.textContent : "";

      var who = document.createElement("div");
      who.className = "lr-who";
      var whoName = card.querySelector(".rs-who b");
      var whoRole = card.querySelector(".rs-who span");
      var nameEl = document.createElement("b");
      nameEl.textContent = whoName ? whoName.textContent : "";
      who.appendChild(nameEl);
      if (whoRole) {
        var roleEl = document.createElement("span");
        roleEl.textContent = whoRole.textContent;
        who.appendChild(roleEl);
      }

      body.appendChild(stars);
      body.appendChild(quote);
      body.appendChild(who);
      wrap.appendChild(body);

      inner.replaceChildren(wrap);
      showLightbox(card, "Opinia rodziny Bajecznych Urwisów");
    };

    var reviewTrack = document.querySelector("[data-rs-track]");
    if (reviewTrack) {
      reviewTrack.addEventListener("click", function (e) {
        var card = e.target.closest(".rs-card");
        if (card) openReview(card);
      });
      reviewTrack.addEventListener("keydown", function (e) {
        if (e.key !== "Enter" && e.key !== " ") return;
        var card = e.target.closest(".rs-card");
        if (card) {
          e.preventDefault();
          openReview(card);
        }
      });
    }

    var closeLb = function () {
      if (!lightbox.classList.contains("open")) return;
      lightbox.classList.remove("open");
      document.body.style.overflow = previousOverflow;
      backgroundState.forEach(function (state) { state.element.inert = state.inert; });
      backgroundState = [];
      if (lightboxTrigger && lightboxTrigger.isConnected) lightboxTrigger.focus({ preventScroll: true });
      lightboxTrigger = null;
    };
    if (lightboxClose) lightboxClose.addEventListener("click", closeLb);
    lightbox.addEventListener("click", function (e) { if (e.target === lightbox) closeLb(); });
    document.addEventListener("keydown", function (e) {
      if (!lightbox.classList.contains("open")) return;
      if (e.key === "Escape") { e.preventDefault(); closeLb(); }
      if (e.key !== "Tab") return;
      var focusable = Array.prototype.slice.call(lightbox.querySelectorAll('button, a[href], [tabindex="0"]'))
        .filter(function (element) { return !element.disabled && !element.hidden; });
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (!first) return;
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      else if (!lightbox.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
    });
  }

  /* ----- Baza wiedzy: strony artykułów (pasek postępu + scrollspy spisu treści) ----- */
  var articleBody = document.querySelector("[data-article-body]");
  if (articleBody) {
    // Pasek postępu czytania — transform: scaleX, aktualizowany w rAF.
    var progressBar = document.querySelector("[data-progress]");
    if (progressBar) {
      var progressTicking = false;
      var updateProgress = function () {
        progressTicking = false;
        var rect = articleBody.getBoundingClientRect();
        var viewport = window.innerHeight;
        var total = rect.height - viewport;
        var read = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 1) : 1;
        progressBar.style.transform = "scaleX(" + read + ")";
      };
      window.addEventListener("scroll", function () {
        if (!progressTicking) {
          progressTicking = true;
          requestAnimationFrame(updateProgress);
        }
      }, { passive: true });
      window.addEventListener("resize", updateProgress, { passive: true });
      window.addEventListener("load", updateProgress, { once: true });
      updateProgress();
    }

    // Scrollspy: podświetlenie aktywnej pozycji spisu treści.
    var tocLinks = Array.prototype.slice.call(document.querySelectorAll("[data-toc] a"));
    var headings = tocLinks
      .map(function (link) {
        var id = (link.getAttribute("href") || "").slice(1);
        return id ? document.getElementById(id) : null;
      })
      .filter(Boolean);

    if (tocLinks.length && headings.length) {
      var setActive = function (id) {
        tocLinks.forEach(function (link) {
          link.classList.toggle("is-active", link.getAttribute("href") === "#" + id);
        });
      };

      if ("IntersectionObserver" in window) {
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
      headings.forEach(function (h) { spy.observe(h); });
      }

      // Klik w spis: natychmiastowe zaznaczenie (scroll dogoni).
      tocLinks.forEach(function (link) {
        link.addEventListener("click", function () {
          setActive((link.getAttribute("href") || "").slice(1));
        });
      });

      setActive(headings[0].id);
    }
  }
})();
