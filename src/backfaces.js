import { $$ } from './utils';

const BACKFACES = Array.prototype.reduce.call($$('.backface'), (obj, template) => {
  const id = template.getAttribute('id');

  obj[id] = template.content.querySelector('svg');

  return obj;
}, {});

export default BACKFACES;
