import "./css/default.css";

import { $ } from './utils';

import Preview from './preview';
import Gallery from './gallery';

document.addEventListener('DOMContentLoaded', () => {
  const drawer = $('#image');

  const preview = new Preview(drawer);
  
  const gallery = new Gallery($('#pogs'), preview);
}, { once: true });
