const $ = (selector, context = document) => context.querySelector(selector);
const $$ = (selector, context = document) => context.querySelectorAll(selector);

const drawer = $('#image');
const drawerPanel = $('.drawer-panel', drawer);

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

const BACKFACES = Array.prototype.reduce.call($$('.backface'), (obj, template) => {
  const id = template.getAttribute('id');

  obj[id] = template.content.querySelector('svg');

  return obj;
}, {});

const off = (el, type, fn, opts = false) => el.removeEventListener(type, fn, opts);

const on = (el, type, fn, opts = false) => {
  el.addEventListener(type, fn, opts);

  return () => off(el, type, fn, opts);
};

const once = (el, type, fn) => on(el, type, fn, { once: true });

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
  })
  .then(() => {
    clearLoad();
    clearError();
  })
  .then(() => img);
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
    this.items = this.buildItems($$('.pog', gallery));

    this.pendingStep = Promise.resolve();

    this.handleKeyDown = throttle(this.handleKeyDown.bind(this), 50);
    this.step = this.step.bind(this);

    on(this.gallery, 'click', this.handleImageClick.bind(this));

    on(document, 'keydown', this.handleKeyDown);

    // TODO: Find a better place for these.
    on($('.preview-image-container'), 'click', e => this.step(1));

    on($('.preview-next'), 'click', e => this.step(1));

    on($('.preview-prev'), 'click', e => this.step(-1));
  }

  buildItems(nodes) {
    return Array.prototype.map.call(nodes, node => ({
      thumbnailSrc: node.getAttribute('data-thumbnail'),
      imageSrc: node.getAttribute('data-image'),
      series: node.getAttribute('data-series'),
      number: node.getAttribute('data-number'),
      backface: node.getAttribute('data-backface'),
      shiny: node.getAttribute('data-shiny'),
    }));
  }

  handleImageClick(e) {
    const pog = e.target.closest('.pog');

    if (!pog) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    this.currentIndex = this.items.findIndex(item => item.number === pog.getAttribute('data-number'));

    this.preview.show(this.items[this.currentIndex]);
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

        return this.preview.show(this.items[this.currentIndex]);
      });
  }
}

class Backface {
  constructor(item) {
    const node = BACKFACES[`backface-${item.backface}`] || BACKFACES['backface-default'];

    this.svg = document.importNode(node, true);
    
    $('tspan', this.svg).textContent = item.number;
    
    this.svgThumnbail = document.importNode(this.svg, true);
  }

  async show() {
    return this.svg;
  }

  thumbnail() {
    return this.svgThumnbail;
  }
}

class Frontface {
  constructor(item) {
    this.item = item;
    
    this.imgFull = new Image();
    this.imgFull.style.background = `url(${item.thumbnailSrc}) #fff no-repeat center center`;
    this.imgFull.style.backgroundSize = 'contain';
    this.imgFull.src = item.imageSrc;
    
    this.imgThumbnail = new Image();
    this.imgThumbnail.src = item.thumbnailSrc;
  }

  async show() {
    return this.imgFull;
  }

  thumbnail() {
    return this.imgThumbnail;
  }
}

class Preview {
  constructor(container) {
    this.container = container;
    this.current = null;
    this.isOpen = false;
    this.isLoading = false;

    this.currentVariantIndex = 0;

    this.open = this.open.bind(this);
    this.close = this.close.bind(this);
    this.show = this.show.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);

    this.number = $('.preview-number', this.container);
    this.details = $('.preview-details', this.container);
    this.imageContainer = $('.preview-image-container', this.container);
    this.variantsContainer = $('.preview-variants', this.container);
    this.variantTemplate = $('.preview-variant-template', this.container);

    on($('.close', this.container), 'click', this.close);

    on($('.overlay'), 'click', e => {
        e.stopPropagation();

        this.close();
      });
  }

  open() {
    if (!this.isOpen) {
      drawer.classList.remove('drawer-closed');

      on(document, 'keyup', this.handleKeyUp);
      on(document, 'keydown', this.handleKeyDown);
    }

    this.isOpen = true;
  }

  close() {
    if (this.isOpen) {
      drawer.classList.add('drawer-closed');

      off(document, 'keyup', this.handleKeyUp);
      off(document, 'keydown', this.handleKeyDown);
    }

    this.isOpen = false;
  }

  addVariants(variants) {
    this.maxVariantIndex = variants.length - 1;

    const fragment = document.createDocumentFragment();

    variants.forEach(variant => {
      const item = document.importNode(this.variantTemplate.content.firstElementChild);

      item.appendChild(variant.thumbnail());

      fragment.appendChild(item);
    });

    clearChildren(this.variantsContainer);

    this.variantsContainer.appendChild(fragment);
  }

  selectVariant(variantIndex) {
    const currentSelected = $('.preview-variant-selected', this.variantsContainer);

    if (currentSelected) {
      currentSelected.classList.remove('preview-variant-selected');
    }

    this.variantsContainer.children.item(variantIndex).classList.add('preview-variant-selected');

    this.variants[variantIndex].show()
      .then(preview => {
        if (this.imageContainer.childElementCount) {
          this.imageContainer.firstElementChild.replaceWith(preview);
        } else {
          this.imageContainer.appendChild(preview);
        }
      });    
  }

  handleKeyUp(evt) {
    const prevVariantIndex = this.currentVariantIndex;

    if (evt.key === 'ArrowDown') {
      this.currentVariantIndex = Math.min(this.currentVariantIndex + 1, this.maxVariantIndex);
    }

    if (evt.key === 'ArrowUp') {
      this.currentVariantIndex = Math.max(this.currentVariantIndex - 1, 0);
    }

    if (prevVariantIndex !== this.currentVariantIndex) {
      this.selectVariant(this.currentVariantIndex);
    }
  }

  handleKeyDown(evt) {
    if (evt.key === 'ArrowDown' || evt.key === 'ArrowUp') {
      evt.preventDefault();
    }
  }

  show(item) {
    this.number.textContent = item.number;
    this.details.textContent = SERIES_CONVERSION[item.series];
    
    this.variants = [
      new Frontface(item),
      new Backface(item),
    ];

    this.addVariants(this.variants);
    
    this.currentVariantIndex = 0;
    this.selectVariant(this.currentVariantIndex);

    this.open();
  }
}

const preview = new Preview($('.drawer-panel'));

const gallery = new Gallery($('#pogs'), preview);