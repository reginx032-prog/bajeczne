/* =========================================================
   Bajeczne Urwisy: interaktywność strony
   ========================================================= */
(function () {
  "use strict";

  /* ---- Rok w stopce ---- */
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---- Nagłówek: cień i chowanie przy scrollu w dół ---- */
  var header = document.querySelector(".site-header");
  var nav = document.getElementById("nav");
  var lastHeaderY = window.scrollY || 0;
  var headerTicking = false;
  var onScroll = function () {
    if (!header || headerTicking) return;
    headerTicking = true;
    requestAnimationFrame(function () {
      var currentY = window.scrollY || 0;
      var menuOpen = nav && nav.classList.contains("open");
      header.classList.toggle("scrolled", currentY > 12);

      if (!menuOpen && currentY > 160 && currentY > lastHeaderY + 6) {
        header.classList.add("is-hidden");
      } else if (currentY < lastHeaderY - 2 || currentY <= 80 || menuOpen) {
        header.classList.remove("is-hidden");
      }

      lastHeaderY = Math.max(currentY, 0);
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
  document.querySelectorAll(".nav-sub-toggle").forEach(function (button) {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var item = button.closest(".has-sub");
      if (!item) return;
      var isOpen = item.classList.toggle("sub-open");
      button.setAttribute("aria-expanded", isOpen ? "true" : "false");
      closeSubmenus(isOpen ? item : null);
      if (header) header.classList.remove("is-hidden");
    });
  });
  document.addEventListener("click", function () {
    closeSubmenus(null);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeSubmenus(null);
  });

  /* ---- Menu mobilne ---- */
  var toggle = document.getElementById("navToggle");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      if (header) header.classList.remove("is-hidden");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Zamknij menu" : "Otwórz menu");
    });
    // Zamknij menu po kliknięciu w link
    nav.querySelectorAll(".nav-links a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        closeSubmenus(null);
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---- Płynne przewijanie do kotwic ---- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var id = link.getAttribute("href");
      if (id === "#" || id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var headerOffset = header ? header.getBoundingClientRect().height + 20 : 90;
      var top = target.getBoundingClientRect().top + window.scrollY - headerOffset;
      window.scrollTo({ top: top, behavior: "smooth" });
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
      mergeItems.forEach(function (el) {
        setMergeProgress(el, getMergeProgress(el));
      });
    };
    var requestMergeUpdate = function () {
      if (mergeTicking) return;
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
  } else {
    mergeItems.forEach(function (el) {
      el.classList.add("in");
      el.style.opacity = "";
      el.style.transform = "";
    });
  }

  /* ---- Animacje wejścia (scroll reveal) ---- */
  var reveals = document.querySelectorAll(".reveal");
  var markVisibleReveals = function () {
    var viewportH = window.innerHeight || document.documentElement.clientHeight;
    var viewportW = window.innerWidth || document.documentElement.clientWidth;
    reveals.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      var nearViewport =
        rect.bottom > -90 &&
        rect.top < viewportH + 90 &&
        rect.right > -160 &&
        rect.left < viewportW + 160;

      if (nearViewport) el.classList.add("in");
    });
  };

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in");
          } else {
            entry.target.classList.remove("in");
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

  /* ---- Podświetlenie aktywnej sekcji w menu (scrollspy) ---- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
  var sections = navLinks
    .map(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.charAt(0) !== "#") return null;
      return document.querySelector(href);
    })
    .filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    var spy = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = "#" + entry.target.id;
            navLinks.forEach(function (a) {
              a.classList.toggle("active", a.getAttribute("href") === id);
            });
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach(function (s) { spy.observe(s); });
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
    var rsReducedMotion = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
      rsStrip.scrollTo({ left: left, behavior: rsReducedMotion ? "auto" : "smooth" });
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
      if (rsReducedMotion) return;
      rsTimer = window.setInterval(function () {
        if (rsHover || rsFocus || rsOffscreen || rsPointerActive || document.hidden) return;
        rsMove(1);
      }, 5000);
    };

    reviewsCarousel.addEventListener("mouseenter", function () { rsHover = true; });
    reviewsCarousel.addEventListener("mouseleave", function () { rsHover = false; });
    reviewsCarousel.addEventListener("focusin", function () { rsFocus = true; });
    reviewsCarousel.addEventListener("focusout", function () {
      rsFocus = reviewsCarousel.contains(document.activeElement);
    });
    if ("IntersectionObserver" in window) {
      var rsObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            rsOffscreen = !entry.isIntersecting;
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
      rsTrack.querySelectorAll(".rs-card").forEach(function (card) {
        var quote = card.querySelector(".rs-quote");
        if (!quote) return;
        card.classList.toggle("is-clamped", quote.scrollHeight > quote.clientHeight + 2);
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
    document.querySelectorAll(".mosaic-tile").forEach(function (item) {
      item.addEventListener("click", function () {
        var img = item.querySelector("img");
        var inner = lightbox.querySelector(".lightbox-inner");
        if (img) {
          var figure = document.createElement("figure");
          var preview = document.createElement("img");

          preview.src = img.src;
          preview.alt = img.alt || "";

          figure.className = "lightbox-figure";
          figure.appendChild(preview);
          inner.replaceChildren(figure);
        }
        lightbox.classList.add("open");
        document.body.style.overflow = "hidden";
      });
    });
    /* pełna opinia w lightboxie */
    var openReview = function (card) {
      var inner = lightbox.querySelector(".lightbox-inner");
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
      lightbox.classList.add("open");
      document.body.style.overflow = "hidden";
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
      lightbox.classList.remove("open");
      document.body.style.overflow = "";
    };
    if (lightboxClose) lightboxClose.addEventListener("click", closeLb);
    lightbox.addEventListener("click", function (e) { if (e.target === lightbox) closeLb(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLb(); });
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

      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) setActive(entry.target.id);
        });
      }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
      headings.forEach(function (h) { spy.observe(h); });

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
