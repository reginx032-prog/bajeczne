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
    this.style = {}; this.inert = false; this.scrollLeft = 0; this.scrollWidth = 1200; this.clientWidth = 400;
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
  doc.body=doc.documentElement.appendChild(new Element('body')); doc.activeElement=doc.body;
  doc.getElementById=id => doc.querySelector('#'+id); doc.createElement=tag => new Element(tag);
  const el=(tag,attrs,parent=doc.body) => parent.appendChild(new Element(tag,attrs));
  const header=el('header',{class:'site-header'}), nav=el('nav',{id:'nav'},header);
  const logo=el('a',{class:'brand brand--logo',href:'#top'},nav);
  const list=el('ul',{class:'nav-links'},nav);
  const homeLink=el('a',{href:'#top'},el('li',{},list));
  const item=el('li',{class:'has-sub'},list);
  const submenuButton=el('button',{class:'nav-sub-toggle','aria-expanded':'false'},item);
  const sub=el('div',{class:'nav-sub'},item), subLink=el('a',{href:'chihuahua.html'},sub);
  const menu=el('button',{id:'navToggle','aria-expanded':'false'},nav);
  const main=el('main',{id:'main-content'});
  const hero=el('section',{id:'top',class:'hero'},main);
  const skip=el('a',{href:'#main-content'});
  const tile=el('button',{class:'mosaic-tile'},main), picture=el('img',{},tile); picture.src='local-photo.jpg'; picture.alt='Puppy';
  const box=el('div',{id:'lightbox',class:'lightbox'}), close=el('button',{id:'lightboxClose'},box);
  el('div',{class:'lightbox-inner'},box);
  const article=el('div',{'data-article-body':''},main); el('span',{'data-progress':''},main);
  const heading=el('h2',{id:'section-one'},article), toc=el('nav',{'data-toc':''},main); el('a',{href:'#section-one'},toc);
  const review=el('div',{'data-reviews-carousel':''}), strip=el('div',{'data-reviews-strip':''},review), track=el('div',{'data-rs-track':''},strip);
  const card=el('article',{class:'rs-card',tabindex:'0'},track), quote=el('p',{class:'rs-quote'},card); quote.textContent='A full review';
  const who=el('div',{class:'rs-who'},card); el('b',{},who).textContent='Family';
  const media={}; const intervals=[]; const scrolls=[]; const history=[];
  const window={innerWidth:390,innerHeight:800,scrollY:0,location:{},history:{pushState(...args){history.push(args)}},
    matchMedia(q){return media[q] ||= {matches:q.includes('reduced-motion') ? reduced : q.includes('hover'),listeners:[],addEventListener(t,fn){this.listeners.push(fn)}}},
    addEventListener(){},setInterval(fn){intervals.push(fn);return intervals.length},clearInterval(){},setTimeout(fn){fn()},
    scrollTo(options){scrolls.push(options)}};
  const context={window,document:doc,requestAnimationFrame:fn=>fn(),getComputedStyle:()=>({columnGap:'20'}),console};
  vm.runInNewContext(script,context,{timeout:2000});
  return {window,media,header,nav,menu,submenuButton,subLink,tile,main,box,close,skip,heading,strip,card,intervals,scrolls,history,logo,homeLink,hero};
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
  s.window.scrollY=2400; s.menu.fire('click'); s.header.classList.add('is-hidden');
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
s=setup(true);
check('reduced motion disables automatic scrolling and smooth anchor movement',()=>{
  assert(doc.documentElement.classList.contains('motion-paused'));s.skip.fire('click');assert.equal(s.scrolls.at(-1).behavior,'auto');
  s.window.scrollY=1900;s.logo.fire('click');assert.equal(s.scrolls.at(-1).top,0);assert.equal(s.scrolls.at(-1).behavior,'auto');
  assert.equal(s.intervals.length,0);
});
check('article initialization works without IntersectionObserver',()=>{assert.equal(doc.querySelector('[data-toc] a').classList.contains('is-active'),true)});
console.log(`${count} interaction checks passed. Layout and rendering are not simulated.`);
