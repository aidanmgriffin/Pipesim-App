export default class particle{
    constructor(x,y, speed) {
        this.x = x;
        this.y = y;
        this.speed = speed;
        this.width = 5;
        this.height = 5;
        this.color = "blue";
    }

    draw(ctx) {
        ctx.fillStyle = this.color;
        this.x += this.speed; 
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}