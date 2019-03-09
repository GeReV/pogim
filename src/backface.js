import { $ } from './utils';

import BACKFACES from './backfaces';

// Number font-size is a function of the number's number of digits.
const BACKFACE_FONT_SIZES = [76, 68, 62, 48];

export default class Backface {
  constructor(item) {
    const node = BACKFACES[`backface-${item.backface}`] || BACKFACES['backface-default'];

    this.svg = document.importNode(node, true);

    const text = $('text', this.svg);

    text.textContent = item.number;

    const numberLength = String(item.number).length;
    const fontSize = BACKFACE_FONT_SIZES[numberLength - 1];

    text.style.fontSize = `${fontSize}px`;

    this.svgThumnbail = document.importNode(this.svg, true);
    this.svgThumnbail.classList.add('preview-variant-backface');
  }

  async show() {
    return this.svg;
  }

  thumbnail() {
    return this.svgThumnbail;
  }
}
