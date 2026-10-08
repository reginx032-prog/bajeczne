// Offline behavioral tests. This DOM model does not render pages or access URLs.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const script = fs.readFileSync(path.join(__dirname, '../script.js'), 'utf8');
let doc;
class Element {
  constructor(tag, attrs = {}) {
    this.tagName = tag.toUpperCase(); this.attrs = {...attrs}; this.children = []; this.listeners = {};
    this.style = {setProperty(key,value){this[key]=value}}; this.inert = false; this.scrollLeft = 0; this.scrollWidth = 1200; this.clientWidth = 400;
    this.clientHeight = 100; this.scrollHeight = 100; this.textContent = '';
    const self = this;
    this.classList = {
      contains(c) {return (self.attrs.class || '').split(/\s+/).includes(c)},
      add(c) {if (!this.contains(c)) self.attrs.class = ((self.attrs.class || '') + ' ' + c).trim()},
      remove(c) {self.attrs.class = (self.attrs.class || '').split(/\s+/).filter(x => x !== c).join(' ')},
      toggle(c, force) {const on = force === undefined ? !this.contains(c) : force; on ? this.add(c) : this.remove(c); return on}
    };
  }
  get className() {return this.attrs.class || ''} set className(v) {this.attrs.class = v}
  get id() {return this.attrs.id || ''}
  get isConnected() {return doc.contains(this)}
  getAttribute(k) {return this.attrs[k] ?? null}
  setAttribute(k,v) {this.attrs[k] = String(v)}
  removeAttribute(k) {delete this.attrs[k]}
  hasAttribute(k) {return k in this.attrs}
  appendChild(c) {c.parent = this; this.children.push(c); return c}
  replaceChildren(...children) {this.children.forEach(c => c.parent = null); this.children = []; children.forEach(c => this.appendChild(c))}
  contains(node) {return !!node && (node === this || this.children.some(c => c.contains(node)))}
  matchesSimple(selector) {
    const attr = [...selector.matchAll(/\[([^\]=^]+)(\^?=)?(?:"([^"]*)")?\]/g)];
    let rest = selector.replace(/\[[^\]]*\]/g, '');
    const tag = rest.match(/^[a-z]+/i); if (tag && this.tagName !== tag[0].toUpperCase()) return false;
    const id = rest.match(/#([\w-]+)/); if (id && this.id !== id[1]) return false;
    if ([...rest.matchAll(/\.([\w-]+)/g)].some(m => !this.classList.contains(m[1]))) return false;
    return attr.every(([,k,op,v]) => op === '=' ? this.getAttribute(k) === v : op === '^=' ? (this.getAttribute(k) || '').startsWith(v) : this.hasAttribute(k));
  }
  matches(selector) {
    return selector.split(',').some(s => {
      const parts=s.trim().split(/\s+/); let node=this;
      if (!node.matchesSimple(parts.pop())) return false;
      while (parts.length) {const part=parts.pop(); node=node.parent; while(node && !node.matchesSimple(part)) node=node.parent; if(!node) return false}
      return true;
    });
  }
  querySelectorAll(selector) {return this.children.flatMap(c => [...(c.matches(selector) ? [c] : []), ...c.querySelectorAll(selector)])}
  querySelector(selector) {return this.querySelectorAll(selector)[0] || null}
  closest(selector) {let n=this; while(n) {if(n.matches(selector)) return n; n=n.parent} return null}
  addEventListener(type, fn) {(this.listeners[type] ||= []).push(fn)}
  fire(type, extra={}) {
    const event={type, target:this, defaultPrevented:false, stopped:false,
      preventDefault(){this.defaultPrevented=true}, stopPropagation(){this.stopped=true}, ...extra};
    let node=this; while(node) {event.currentTarget=node; (node.listeners[type] || []).forEach(fn => fn(event)); if(event.stopped) break; node=node.parent}
    return event;
  }
  focus() {const old=doc.activeElement; doc.activeElement=this; if(old && old!==this) old.fire('focusout',{relatedTarget:this}); this.fire('focusin',{relatedTarget:old})}
  getBoundingClientRect() {return {width:300,height:1200,top:0,bottom:1200,left:0,right:300}}
  scrollTo(options) {this.scrollLeft=options.left || 0}
}
function setup(reduced=false) {
  doc = new Element('document'); doc.documentElement = doc.appendChild(new Element('html'));
  doc.documentElement.scrollHeight = 10000;
  doc.body=doc.documentElement.appendChild(new Element('body')); doc.activeElement=doc.body;
  doc.getElementById=id => doc.querySelector('#'+id); doc.createElement=tag => new Element(tag);
  const el=(tag,attrs,parent=doc.body) => parent.appendChild(new Element(tag,attrs));
  const header=el('header',{class:'site-header'}), nav=el('nav',{id:'nav'},header);
  const logo=el('a',{class:'brand brand--logo',href:'#top'},nav);
  const list=el('ul',{class:'nav-links'},nav);
  const homeLink=el('a',{href:'#top'},el('li',{},list));
  const puppiesLink=el('a',{href:'#szczenieta'},el('li',{},list));
  const aboutLink=el('a',{href:'#o-hodowli'},el('li',{},list));
  const item=el('li',{class:'has-sub'},list);
  const submenuButton=el('button',{class:'nav-sub-toggle','aria-expanded':'false'},item);
  const sub=el('div',{class:'nav-sub'},item), subLink=el('a',{href:'chihuahua.html'},sub);
  const menu=el('button',{id:'navToggle','aria-expanded':'false'},nav);
  const main=el('main',{id:'main-content'});
  const hero=el('section',{id:'top',class:'hero'},main);
  const puppies=el('section',{id:'szczenieta'},main), about=el('section',{id:'o-hodowli'},main);
  const malformedLink=el('a',{href:'#%zz'},main);
  const skip=el('a',{href:'#main-content'});
  const tile=el('button',{class:'mosaic-tile'},main), picture=el('img',{},tile); picture.src='local-photo.jpg'; picture.alt='Puppy';
  const box=el('div',{id:'lightbox',class:'lightbox'}), close=el('button',{id:'lightboxClose'},box);
  el('div',{class:'lightbox-inner'},box);
  const article=el('div',{'data-article-body':''},main); el('span',{'data-progress':''},main);
  const heading=el('h2',{id:'section-one'},article), toc=el('nav',{'data-toc':''},main); el('a',{href:'#section-one'},toc);
  const review=el('div',{'data-reviews-carousel':''}), strip=el('div',{'data-reviews-strip':''},review), track=el('div',{'data-rs-track':''},strip);
  const card=el('article',{class:'rs-card',tabindex:'0'},track), quote=el('p',{class:'rs-quote'},card); quote.textContent='A full review';
  const who=el('div',{class:'rs-who'},card); el('b',{},who).textContent='Family';
  const media={}; const intervals=[]; const activeIntervals=new Set(); const scrolls=[]; const history=[]; const timers=new Map(); let timerId=0;
  const listeners={};
  const window={innerWidth:390,innerHeight:800,scrollY:0,location:{hash:''},history:{pushState(...args){history.push(args);window.location.hash=args[2]}},
    matchMedia(q){return media[q] ||= {matches:q.includes('reduced-motion') ? reduced : q.includes('hover'),listeners:[],addEventListener(t,fn){this.listeners.push(fn)}}},
    addEventListener(type,fn){(listeners[type] ||= []).push(fn)},fire(type,event={}){(listeners[type] || []).forEach(fn=>fn(event))},
    setInterval(fn){intervals.push(fn);activeIntervals.add(intervals.length);return intervals.length},clearInterval(id){activeIntervals.delete(id)},
    setTimeout(fn){timers.set(++timerId,fn);return timerId},clearTimeout(id){timers.delete(id)},
    scrollTo(options){scrolls.push(options)}};
  const flushTimers=()=>{const pending=[...timers.values()];timers.clear();pending.forEach(fn=>fn())};
  const geometry=(node,y,height=900)=>{node.getBoundingClientRect=()=>({top:y-window.scrollY,bottom:y-window.scrollY+height,height,width:300,left:0,right:300})};
  header.getBoundingClientRect=()=>({height:88,top:0,bottom:88});
  geometry(hero,88);geometry(puppies,2000);geometry(about,7000);
  const context={window,document:doc,requestAnimationFrame:fn=>fn(),getComputedStyle:()=>({columnGap:'20'}),console};
  vm.runInNewContext(script,context,{timeout:2000});
  return {window,media,header,nav,menu,submenuButton,subLink,tile,main,box,close,skip,heading,strip,card,intervals,activeIntervals,scrolls,history,logo,homeLink,hero,puppiesLink,aboutLink,puppies,about,flushTimers,geometry,malformedLink};
}
let count=0;
function check(name, fn) {fn(); count++; console.log('PASS '+name)}
let s=setup();
check('mobile menu opens, Escape closes and restores focus',()=>{
  s.menu.fire('click'); assert(s.nav.classList.contains('open'));
  s.submenuButton.fire('click'); assert.equal(s.submenuButton.getAttribute('aria-expanded'),'true');
  s.subLink.focus(); doc.fire('keydown',{key:'Escape'});
  assert(!s.nav.classList.contains('open')); assert.equal(doc.activeElement,s.menu);
  assert.equal(s.menu.getAttribute('aria-label'),'Otwórz menu');
});
check('outside click closes mobile menu',()=>{s.menu.fire('click'); s.main.fire('click'); assert(!s.nav.classList.contains('open'))});
check('ArrowDown opens submenu; Escape restores trigger',()=>{
  s.submenuButton.focus(); s.submenuButton.fire('keydown',{key:'ArrowDown'}); assert.equal(doc.activeElement,s.subLink);
  doc.fire('keydown',{key:'Escape'}); assert.equal(doc.activeElement,s.submenuButton); assert.equal(s.submenuButton.getAttribute('aria-expanded'),'false');
});
check('menu link clears menu state and label',()=>{s.menu.fire('click');s.subLink.fire('click');assert.equal(s.menu.getAttribute('aria-expanded'),'false');assert.equal(s.menu.getAttribute('aria-label'),'Otwórz menu')});
check('logo returns to the page start, closes mobile menu and reveals header',()=>{
  s.window.scrollY=2400; s.menu.fire('click');
  assert(s.logo.fire('click').defaultPrevented);
  assert.equal(s.scrolls.at(-1).top,0); assert.equal(s.history.at(-1)[2],'#top');
  assert.equal(doc.activeElement,s.hero); assert(!s.nav.classList.contains('open'));
  assert(!s.header.classList.contains('is-hidden')); assert.equal(s.menu.getAttribute('aria-expanded'),'false');
});
check('home menu link returns to the top again when the fragment is already top',()=>{
  s.window.scrollY=1600; s.homeLink.fire('click');
  assert.equal(s.scrolls.at(-1).top,0); assert.equal(s.history.at(-1)[2],'#top');
  assert.equal(doc.activeElement,s.hero);
});
check('modified logo clicks retain native new-tab navigation',()=>{
  const previousScrolls=s.scrolls.length;
  assert(!s.logo.fire('click',{ctrlKey:true}).defaultPrevented);
  assert(!s.logo.fire('click',{metaKey:true}).defaultPrevented);
  assert.equal(s.scrolls.length,previousScrolls);
});
check('gallery takes focus, traps Tab, closes and restores focus/scroll',()=>{
  doc.body.style.overflow='auto'; s.tile.focus();s.tile.fire('click');
  assert(s.box.classList.contains('open'));assert.equal(doc.activeElement,s.close);assert.equal(s.main.inert,true);
  assert(s.close.fire('keydown',{key:'Tab'}).defaultPrevented);assert.equal(doc.activeElement,s.close);
  assert(s.close.fire('keydown',{key:'Tab',shiftKey:true}).defaultPrevented);
  doc.fire('keydown',{key:'Escape'});assert(!s.box.classList.contains('open'));assert.equal(doc.activeElement,s.tile);
  assert.equal(s.main.inert,false);assert.equal(doc.body.style.overflow,'auto');
});
check('backdrop and close button both close gallery',()=>{
  s.tile.fire('click');s.box.fire('click');assert(!s.box.classList.contains('open'));
  s.tile.fire('click');s.close.fire('click');assert(!s.box.classList.contains('open'));
});
check('review keyboard activation opens correct dialog and restores focus',()=>{
  s.card.focus();s.card.fire('keydown',{key:'Enter'});assert(s.box.classList.contains('open'));
  assert(s.box.getAttribute('aria-label').startsWith('Opinia'));
  const content=s.box.querySelector('.lightbox-inner');assert.equal(content.getAttribute('tabindex'),'0');
  content.focus();assert(content.fire('keydown',{key:'Tab'}).defaultPrevented);assert.equal(doc.activeElement,s.close);
  s.close.fire('click');assert.equal(doc.activeElement,s.card);
});
check('skip link moves focus and records a usable URL fragment',()=>{
  s.skip.fire('click');assert.equal(doc.activeElement,s.main);assert.equal(s.history.at(-1)[2],'#main-content');
});
s=setup();
check('section navigation closes mobile menu and uses the measured header offset',()=>{
  s.menu.fire('click');s.aboutLink.fire('click');
  assert(!s.nav.classList.contains('open'));assert.equal(doc.activeElement,s.about);
  assert.equal(s.scrolls.at(-1).top,6892);assert.equal(s.scrolls.at(-1).behavior,'smooth');
  assert.equal(doc.documentElement.style['--anchor-offset'],'108px');
  assert(s.aboutLink.classList.contains('active'));
});
check('intermediate sections do not steal the active menu item during navigation',()=>{
  s.window.scrollY=2400;s.window.fire('scroll');
  assert(s.aboutLink.classList.contains('active'));assert(!s.puppiesLink.classList.contains('active'));
  assert(!s.header.classList.contains('is-hidden'));
  s.window.scrollY=6892;s.window.fire('scroll');s.flushTimers();
  assert(s.aboutLink.classList.contains('active'));
  s.window.scrollY=2400;s.window.fire('scroll');
  assert(s.puppiesLink.classList.contains('active'));assert(!s.aboutLink.classList.contains('active'));
});
check('quick consecutive clicks replace the target and never queue a second scroll',()=>{
  s.aboutLink.fire('click');s.puppiesLink.fire('click');
  assert(s.puppiesLink.classList.contains('active'));assert.equal(s.scrolls.at(-1).top,1892);
  const calls=s.scrolls.length;s.window.scrollY=1892;s.window.fire('scroll');s.flushTimers();
  assert.equal(s.scrolls.length,calls);assert(s.puppiesLink.classList.contains('active'));
});
check('clicking the same section again does not duplicate browser history',()=>{
  const entries=s.history.length;s.puppiesLink.fire('click');
  assert.equal(s.history.length,entries);assert.equal(s.scrolls.at(-1).top,1892);
  s.flushTimers();assert(s.puppiesLink.classList.contains('active'));
});
check('manual scrolling cancels the active-item lock without forcing another jump',()=>{
  for(const event of ['wheel','touchstart']) {
    s.aboutLink.fire('click');s.window.scrollY=2400;s.window.fire('scroll');
    const calls=s.scrolls.length;s.window.fire(event);
    assert(s.puppiesLink.classList.contains('active'));assert.equal(s.scrolls.length,calls);
  }
  s.aboutLink.fire('click');doc.fire('keydown',{key:'PageUp'});assert(s.puppiesLink.classList.contains('active'));
});
check('history navigation updates the menu without overriding native scroll restoration',()=>{
  s.aboutLink.fire('click');s.window.scrollY=0;
  const calls=s.scrolls.length;s.window.fire('popstate');s.window.fire('hashchange');
  assert(s.homeLink.classList.contains('active'));assert.equal(s.scrolls.length,calls);
});
check('resizing recalculates the anchor offset and retains a visible sticky header',()=>{
  s.header.getBoundingClientRect=()=>({height:102});s.window.innerWidth=1366;s.window.fire('resize');
  s.aboutLink.fire('click');assert.equal(s.scrolls.at(-1).top,6878);
  assert.equal(doc.documentElement.style['--anchor-offset'],'122px');
  s.window.scrollY=6000;s.window.fire('scroll');assert(!s.header.classList.contains('is-hidden'));
});
check('malformed or modified anchor links do not trigger scripted navigation',()=>{
  const calls=s.scrolls.length;assert(!s.malformedLink.fire('click').defaultPrevented);
  assert(!s.aboutLink.fire('click',{ctrlKey:true}).defaultPrevented);assert.equal(s.scrolls.length,calls);
});
s=setup();
check('background tabs stop the review timer and pause the photo animation',()=>{
  assert.equal(s.activeIntervals.size,1);
  doc.hidden=true;doc.fire('visibilitychange');
  assert.equal(s.activeIntervals.size,0);assert(doc.documentElement.classList.contains('page-hidden'));
  doc.hidden=false;doc.fire('visibilitychange');
  assert.equal(s.activeIntervals.size,1);assert(!doc.documentElement.classList.contains('page-hidden'));
  doc.fire('visibilitychange');assert.equal(s.activeIntervals.size,1);
});
check('changing reduced-motion preference stops and resumes a single timer',()=>{
  const query=s.media['(prefers-reduced-motion: reduce)'];
  query.matches=true;query.listeners.forEach(fn=>fn({matches:true}));
  assert.equal(s.activeIntervals.size,0);
  query.matches=false;query.listeners.forEach(fn=>fn({matches:false}));
  assert.equal(s.activeIntervals.size,1);
});
const scrollHeader = y => {s.window.scrollY=y;s.window.fire('scroll')};
const headerHidden = () => s.header.classList.contains('is-hidden');
s=setup();
check('header stays at the top, hides on downward scroll and returns on upward scroll',()=>{
  assert(!headerHidden());scrollHeader(60);assert(!headerHidden());
  scrollHeader(120);assert(headerHidden());scrollHeader(110);assert(!headerHidden());
  assert.equal(doc.documentElement.style['--anchor-offset'],'108px');
});
check('small direction changes do not flicker; sustained small steps reveal and hide the header',()=>{
  scrollHeader(160);assert(headerHidden());
  for(const y of [157,159,156,152]) {scrollHeader(y);assert(headerHidden())}
  scrollHeader(151);assert(!headerHidden());
  for(const y of [154,157]) {scrollHeader(y);assert(!headerHidden())}
  scrollHeader(159);assert(headerHidden());
});
check('top and bottom elastic overscroll do not cause false direction changes',()=>{
  scrollHeader(0);assert(!headerHidden());scrollHeader(-80);assert(!headerHidden());
  scrollHeader(0);assert(!headerHidden());scrollHeader(8900);assert(headerHidden());
  scrollHeader(9250);assert(headerHidden());scrollHeader(9200);assert(headerHidden());
  scrollHeader(9190);assert(!headerHidden());
});
s=setup();
check('mobile menu stays visible while open and scrolling resumes after closing it',()=>{
  scrollHeader(300);assert(headerHidden());s.menu.fire('click');assert(!headerHidden());
  scrollHeader(500);assert(!headerHidden());s.menu.fire('click');s.main.focus();
  scrollHeader(520);assert(headerHidden());
});
check('desktop submenu stays visible while open',()=>{
  s.media['(min-width: 1281px)'].matches=true;
  s.submenuButton.closest('.has-sub').fire('mouseenter');assert(!headerHidden());
  scrollHeader(700);assert(!headerHidden());
  s.submenuButton.closest('.has-sub').fire('mouseleave');scrollHeader(720);assert(headerHidden());
});
check('keyboard focus restores the hidden header and keeps navigation reachable',()=>{
  s.homeLink.focus();assert(!headerHidden());scrollHeader(900);assert(!headerHidden());
  s.main.focus();scrollHeader(920);assert(headerHidden());
});
check('resizing reveals the header and resets the scroll threshold',()=>{
  s.window.fire('resize');assert(!headerHidden());scrollHeader(922);assert(!headerHidden());
  scrollHeader(930);assert(headerHidden());
});
check('anchor navigation reveals the header, then manual scrolling can hide it again',()=>{
  s.puppiesLink.fire('click');assert(!headerHidden());assert.equal(s.scrolls.at(-1).top,1892);
  scrollHeader(1892);assert(!headerHidden());s.flushTimers();
  scrollHeader(1904);assert(headerHidden());scrollHeader(1894);assert(!headerHidden());
});
s=setup(true);
check('header direction behavior also works with reduced motion enabled',()=>{
  scrollHeader(300);assert(headerHidden());scrollHeader(288);assert(!headerHidden());
});
check('reduced motion disables automatic scrolling and smooth anchor movement',()=>{
  assert(doc.documentElement.classList.contains('motion-paused'));s.skip.fire('click');assert.equal(s.scrolls.at(-1).behavior,'auto');
  s.window.scrollY=1900;s.logo.fire('click');assert.equal(s.scrolls.at(-1).top,0);assert.equal(s.scrolls.at(-1).behavior,'auto');
  assert.equal(s.intervals.length,0);
});
check('article initialization works without IntersectionObserver',()=>{assert.equal(doc.querySelector('[data-toc] a').classList.contains('is-active'),true)});
console.log(`${count} interaction checks passed. Layout and rendering are not simulated.`);
