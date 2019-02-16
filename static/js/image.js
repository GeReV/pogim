const drawer = document.querySelector('#image');
const drawerPanel = drawer.querySelector('.drawer-panel');

const largeImage = new Image();

function once(el, type, fn) {
  return el.addEventListener(type, function listener(e) {
    fn(e);

    el.removeEventListener(type, listener);
  });
}

function imageLoad(img, src, callback) {
  once(img, 'load', callback);
  img.src = src;
}

function clearChildren(el) {
  while (el.lastChild) {
    el.removeChild(el.lastChild);
  }
}

document.querySelector('#pogs')
  .addEventListener('click', e => {
    const pog = e.target.closest('.pog');

    if (!pog) {
      return;
    }

    const thumbnailSrc = pog.querySelector('img').getAttribute('src');
    const imageSrc = pog.getAttribute('href');

    e.preventDefault();
    e.stopPropagation();

    clearChildren(drawerPanel);

    const image = new Image();
    image.classList.add('drawer-panel-image');

    drawerPanel.appendChild(image);

    imageLoad(image, thumbnailSrc, () => {
      drawer.classList.remove('drawer-closed');
    });

    imageLoad(largeImage, imageSrc, () => {
      image.src = largeImage.src;
    });
  });

drawer.querySelector('.overlay')
  .addEventListener('click', e => {
    e.stopPropagation();

    drawer.classList.add('drawer-closed');
  });