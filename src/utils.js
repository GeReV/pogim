export const $ = (selector, context = document) => context.querySelector(selector);
export const $$ = (selector, context = document) => context.querySelectorAll(selector);

export const off = (el, type, fn, opts = false) => el.removeEventListener(type, fn, opts);

export const on = (el, type, fn, opts = false) => {
  el.addEventListener(type, fn, opts);

  return () => off(el, type, fn, opts);
};

export const once = (el, type, fn) => on(el, type, fn, { once: true });

export function throttle(callback, wait, immediate = false) {
  let timeout = null;
  let initialCall = true;

  return function () {
    const callNow = immediate && initialCall;
    const next = () => {
      callback.apply(this, arguments);
      timeout = null;
    };

    if (callNow) {
      initialCall = false;
      next();
    }

    if (!timeout) {
      timeout = setTimeout(next, wait);
    }
  };
}

export function imageLoad(img, src) {
  let clearLoad;
  let clearError;

  return new Promise((resolve, reject) => {
    clearLoad = once(img, 'load', resolve);
    clearError = once(img, 'error', reject);

    img.src = src;
  })
  .then(() => {
    clearLoad();
    clearError();
  })
  .then(() => img);
}

export function clearChildren(el) {
  while (el.lastChild) {
    el.removeChild(el.lastChild);
  }
}
