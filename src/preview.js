import { $, on, off, clearChildren } from './utils';

import Backface from './backface';
import Frontface from './frontface';

import SERIES_CONVERSION from './series';

export default class Preview {
  constructor(drawer) {
    this.drawer = drawer;
    this.container = drawer.querySelector('.drawer-panel');
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
    this.downloadLinkPng = $('.preview-download-png', this.container);
    this.downloadLinkJpg = $('.preview-download-jpg', this.container);
    this.imageContainer = $('.preview-image-container', this.container);
    this.variantsContainer = $('.preview-variants', this.container);
    this.variantTemplate = $('.preview-variant-template', this.container);

    on(this.variantsContainer, 'click', this.handleVariantClick.bind(this));

    on($('.close', this.container), 'click', this.close);

    on($('.overlay'), 'click', e => {
        e.stopPropagation();

        this.close();
      });
  }

  open() {
    if (!this.isOpen) {
      this.drawer.classList.remove('drawer-closed');

      on(document, 'keyup', this.handleKeyUp);
      on(document, 'keydown', this.handleKeyDown);
    }

    this.isOpen = true;
  }

  close() {
    if (this.isOpen) {
      this.drawer.classList.add('drawer-closed');

      off(document, 'keyup', this.handleKeyUp);
      off(document, 'keydown', this.handleKeyDown);
    }

    this.isOpen = false;
  }

  handleVariantClick(e) {
    const clickedVariant = e.target.closest('.preview-variant');

    if (clickedVariant) {
      this.currentVariantIndex = Array.prototype.indexOf.call(this.variantsContainer.children, clickedVariant);

      this.selectVariant(this.currentVariantIndex);
    }

    e.preventDefault();
    e.stopPropagation();
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

    const preview = this.variants[variantIndex].show();

    if (this.imageContainer.childElementCount) {
      this.imageContainer.firstElementChild.replaceWith(preview);
    } else {
      this.imageContainer.appendChild(preview);
    }
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
    this.downloadLinkPng.setAttribute('href', item.originalSrc);
    this.downloadLinkJpg.setAttribute('href', item.imageSrc);
    
    this.variants = [
      new Frontface(item),
      new Backface(item),
    ];

    this.addVariants(this.variants);
    
    this.selectVariant(this.currentVariantIndex);

    this.open();
  }
}
