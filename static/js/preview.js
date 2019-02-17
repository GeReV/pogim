const drawer = document.querySelector('#image');
const drawerPanel = drawer.querySelector('.drawer-panel');

const largeImage = new Image();

const SERIES_CONVERSION = {
  green: 'הסדרה הירוקה',
  red: 'הסדרה האדומה',
  blue: 'הסדרה הכחולה',
  purple: 'הסדרה הסגולה',
  orange: 'הסדרה הכתומה',
  pink: 'הסדרה הורודה',
  poalim: 'בנק פועלים',
  brown: 'הסדרה החומה',
  black: 'הסדרה השחורה (סונול)',
  gray: 'הסדרה האפורה',
  turquoise: 'סדרת הטורקיז',
  psycho: 'פסיכי בריבוע',
  gold: 'סדרת הזהב (באדי תנובה)',
  dominos: 'הסדרה האמריקאית (דומינו\'ס פיצה)',
  "comedy-store": 'הקומדי סטור',
  "comedy-store-yellow": 'הקומדי סטור (סדרה צהובה)',
  crazies: 'סדרת המוטרפים',
  bushido: 'ענקי הבושידו',
  yellow: 'הסדרה הצהובה',
  horospog: 'הורוספוג',
};

function once(el, type, fn) {
  el.addEventListener(type, fn, { once: true });

  return () => el.removeEventListener(type, fn, { once: true });
}

function throttle(callback, wait, immediate = false) {
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

function imageLoad(img, src) {
  let clearLoad;
  let clearError;

  return new Promise((resolve, reject) => {
    clearLoad = once(img, 'load', resolve);
    clearError = once(img, 'error', reject);

    img.src = src;
  }).then(() => {
    clearLoad();
    clearError();
  });
}

function clearChildren(el) {
  while (el.lastChild) {
    el.removeChild(el.lastChild);
  }
}

class Gallery {
  constructor(gallery, preview) {
    this.gallery = gallery;
    this.preview = preview;
    this.items = gallery.querySelectorAll('.pog');

    this.pendingStep = Promise.resolve();

    this.handleKeyDown = throttle(this.handleKeyDown.bind(this), 50);
    this.step = this.step.bind(this);

    this.gallery.addEventListener('click', this.handleImageClick.bind(this));

    document.addEventListener('keydown', this.handleKeyDown);

    // TODO: Find a better place for these.
    document.querySelector('.preview-image')
      .addEventListener('click', e => this.step(1));

    document.querySelector('.preview-next')
      .addEventListener('click', e => this.step(1));

    document.querySelector('.preview-prev')
      .addEventListener('click', e => this.step(-1));
  }

  handleImageClick(e) {
    const pog = e.target.closest('.pog');

    if (!pog) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    this.currentIndex = Array.prototype.indexOf.call(this.items, pog);

    this.preview.show(pog);
  }

  handleKeyDown(e) {
    if (e.key === 'ArrowLeft') {
      this.step(1);
    }

    if (e.key === 'ArrowRight') {
      this.step(-1);
    }

    if (e.key === 'Escape') {
      this.preview.close();
    }
  }

  step(offset) {
    this.pendingStep = this.pendingStep
      .then(() => {
        const nextIndex = (this.currentIndex + offset + this.items.length) % this.items.length;

        this.currentIndex = nextIndex;

        return this.preview.show(this.items.item(this.currentIndex));
      });
  }
}

class Preview {
  constructor(container) {
    this.container = container;
    this.current = null;
    this.isOpen = false;
    this.isLoading = false;

    this.open = this.open.bind(this);
    this.close = this.close.bind(this);
    this.show = this.show.bind(this);

    this.image = this.container.querySelector('.preview-image');
    this.number = this.container.querySelector('.preview-number');
    this.details = this.container.querySelector('.preview-details');

    this.container.querySelector('.close')
      .addEventListener('click', this.close);

    document.querySelector('.overlay')
      .addEventListener('click', e => {
        e.stopPropagation();

        this.close();
      });
  }

  open() {
    if (!this.isOpen) {
      drawer.classList.remove('drawer-closed');
    }

    this.isOpen = true;
  }

  close() {
    if (this.isOpen) {
      drawer.classList.add('drawer-closed');
    }

    this.isOpen = false;
  }

  show(el) {
    this.current = el;

    const thumbnailSrc = this.current.getAttribute('data-thumbnail');
    const imageSrc = this.current.getAttribute('data-image');
    const series = this.current.getAttribute('data-series');
    const number = this.current.getAttribute('data-number');
    const shiny = this.current.getAttribute('data-shiny');

    this.number.textContent = number;
    this.details.textContent = SERIES_CONVERSION[series];

    imageLoad(this.image, thumbnailSrc)
      .then(this.open);

    // TODO: Should be possible to navigate once lo-res image displayed and abort load.
    return imageLoad(largeImage, imageSrc)
      .then(() => {
        this.image.src = largeImage.src;
      });
  }
}

const preview = new Preview(document.querySelector('.drawer-panel'));

const gallery = new Gallery(document.querySelector('#pogs'), preview);