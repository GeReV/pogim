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
    this.items = this.buildItems(gallery.querySelectorAll('.pog'));

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

  buildItems(nodes) {
    return Array.prototype.map.call(nodes, node => ({
      thumbnailSrc: node.getAttribute('data-thumbnail'),
      imageSrc: node.getAttribute('data-image'),
      series: node.getAttribute('data-series'),
      number: node.getAttribute('data-number'),
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

class Preview {
  constructor(container) {
    this.container = container;
    this.current = null;
    this.isOpen = false;
    this.isLoading = false;
    this.backfaces = this.buildBackfaces(this.container.querySelectorAll('.backface'));

    this.currentVariantIndex = 0;

    this.open = this.open.bind(this);
    this.close = this.close.bind(this);
    this.show = this.show.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);

    this.image = this.container.querySelector('.preview-image');
    this.number = this.container.querySelector('.preview-number');
    this.details = this.container.querySelector('.preview-details');
    this.variants = this.container.querySelector('.preview-variants');

    this.maxVariantIndex = this.variants.childElementCount - 1;

    this.variantsPrimary = this.variants.querySelector('.preview-variant-primary');
    this.variantsBackface = this.variants.querySelector('.preview-variant-backface');

    this.container.querySelector('.close')
      .addEventListener('click', this.close);

    document.querySelector('.overlay')
      .addEventListener('click', e => {
        e.stopPropagation();

        this.close();
      });
  }

  buildBackfaces(backfaces) {
    return Array.prototype.reduce.call(backfaces, (obj, template) => {
      const id = template.getAttribute('id');

      obj[id] = template.content;

      return obj;
    }, {});
  }

  open() {
    if (!this.isOpen) {
      drawer.classList.remove('drawer-closed');

      document.addEventListener('keyup', this.handleKeyUp);
      document.addEventListener('keydown', this.handleKeyDown);
    }

    this.isOpen = true;
  }

  close() {
    if (this.isOpen) {
      drawer.classList.add('drawer-closed');

      document.removeEventListener('keyup', this.handleKeyUp);
      document.removeEventListener('keydown', this.handleKeyDown);
    }

    this.isOpen = false;
  }

  selectVariant(variantIndex) {
    const currentSelected = this.variants.querySelector('.preview-variant-selected');

    if (currentSelected) {
      currentSelected.classList.remove('preview-variant-selected');
    }

    this.variants.children.item(variantIndex).classList.add('preview-variant-selected');
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

  setPrimaryVariant(src) {
    this.variantsPrimary.querySelector('img').src = src;
  }

  setBackfaceVariant(backface, number) {
    clearChildren(this.variantsBackface);

    const svg = document.importNode(backface, true);
    svg.querySelector('tspan').textContent = number;

    this.variantsBackface.appendChild(svg);
  }

  show(item) {
    this.currentItem = item;

    this.number.textContent = item.number;
    this.details.textContent = SERIES_CONVERSION[item.series];

    this.setPrimaryVariant(item.thumbnailSrc);

    this.setBackfaceVariant(this.backfaces['backface-standard'], item.number);

    imageLoad(largeImage, item.imageSrc)
      .then(() => {
        if (this.currentItem.number === item.number) {
          this.image.src = largeImage.src;
        }
      });

    return imageLoad(this.image, item.thumbnailSrc)
      .then(this.open);
  }
}

const preview = new Preview(document.querySelector('.drawer-panel'));

const gallery = new Gallery(document.querySelector('#pogs'), preview);