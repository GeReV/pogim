export default class Frontface {
  constructor(item) {
    this.item = item;
    
    this.imgFull = new Image();
    this.imgFull.style.background = `url(${item.thumbnailSrc}) no-repeat center center`;
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
