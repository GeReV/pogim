import "./css/default.css";

import { $, on, trackPageView } from './utils';

import Preview from './preview';
import Gallery from './gallery';

on(document, 'DOMContentLoaded', () => {
  const drawer = $('#image');

  const preview = new Preview(drawer);

  const gallery = new Gallery($('#pogs'), preview);
}, { once: true });

on(window, 'popstate', trackPageView);