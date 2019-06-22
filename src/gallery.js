import { $, $$, on, throttle, pushHistory } from './utils';

export default class Gallery {
  constructor(gallery, preview) {
    this.gallery = gallery;
    this.preview = preview;
    this.items = this.buildItems($$('.pog', gallery));

    this.pendingStep = Promise.resolve();

    this.handleKeyDown = throttle(this.handleKeyDown.bind(this), 50);
    this.step = this.step.bind(this);

    on(this.gallery, 'click', this.handleImageClick.bind(this));

    on(document, 'keydown', this.handleKeyDown);

    on(window, 'popstate', this.handleHistoryPopState.bind(this));

    // TODO: Find a better place for these.
    on($('.preview-image-container'), 'click', e => this.step(1));

    on($('.preview-next'), 'click', e => this.step(1));

    on($('.preview-prev'), 'click', e => this.step(-1));

    this.handleStartupUrl();
  }

  get currentItem() {
    return this.items[this.currentIndex];
  }

  buildItems(nodes) {
    return Array.prototype.map.call(nodes, node => ({
      thumbnailSrc: node.getAttribute('data-thumbnail'),
      imageSrc: node.getAttribute('data-image'),
      originalSrc: node.getAttribute('href'),
      series: node.getAttribute('data-series'),
      number: node.getAttribute('data-number'),
      backface: node.getAttribute('data-backface'),
      shiny: node.getAttribute('data-shiny'),
      missing: node.getAttribute('data-missing'),
    }));
  }

  findItemIndex(number) {
    return this.items.findIndex(item => item.number === number);
  }

  handleStartupUrl() {
    const number = new URLSearchParams(window.location.search).get('pog');

    if (!number) {
      return;
    }

    this.currentIndex = this.findItemIndex(number);

    this.preview.show(this.currentItem);
  }

  handleHistoryPopState(e) {
    e.preventDefault();
    e.stopPropagation();

    const number = new URLSearchParams(window.location.search).get('pog');

    if (!number) {
      this.preview.close();

      return;
    }

    this.currentIndex = this.findItemIndex(number);

    this.preview.show(this.currentItem);
  }

  handleImageClick(e) {
    const pog = e.target.closest('.pog');

    if (!pog) {
      return;
    }

    e.preventDefault();
    e.stopPropagation();

    this.currentIndex = this.findItemIndex(pog.getAttribute('data-number'));

    const item = this.currentItem;

    pushHistory(item.number);

    this.preview.show(item, true);
  }

  handleKeyDown(e) {
    if (e.key === 'ArrowLeft') {
      this.step(1);
    }

    if (e.key === 'ArrowRight') {
      this.step(-1);
    }
  }

  step(offset) {
    if (!this.preview.isOpen) {
      return;
    }

    this.pendingStep = this.pendingStep
      .then(() => {
        const nextIndex = (this.currentIndex + offset + this.items.length) % this.items.length;

        this.currentIndex = nextIndex;

        const item = this.currentItem;

        pushHistory(item.number);

        return this.preview.show(item);
      });
  }
}
