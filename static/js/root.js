export default class Root  {
    constructor(x,y, particleController) {
        this.x = x;
        this.y = y;
        this.particleController = particleController;
        this.width = 5;
        this.height = 50;
        this.speed = 4;

        document.addEventListener('keydown', this.keydown);
        document.addEventListener('keyup', this.keyup);
    }

    draw(ctx) {
        this.move();
        ctx.strokeStyle = 'black';
        ctx.fillstyle = 'black';
        ctx.strokeRect(this.x, this.y, this.width, this.height);
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.strokeRect(this.x, this.y, 500, 5)
        ctx.fillRect(this.x, this.y, 500, 5);
        ctx.strokeRect(this.x, this.y + this.height, 500, 5)
        ctx.fillRect(this.x, this.y + this.height, 500, 5);
        ctx.strokeRect(this.x + 495, this.y, this.width, this.height);
        ctx.fillRect(this.x + 495, this.y, this.width, this.height);

        this.shoot();
    }

    move() {
        if(this.upPressed) {
            this.y -= this.speed;
        }
        if(this.downPressed) {
            this.y += this.speed;
        }
        if(this.leftPressed) {
            this.x -= this.speed;
        }   
        if(this.rightPressed) {
            this.x += this.speed;
        }
    }

    shoot() {
        // if(this.shootPressed) {
            console.log('shoot');
            const speed = 5;
            const delay = 7;
            const damage = 1;
            const particleX = this.x + this.width / 2;
            const particleY = this.y + this.height / 2;
            this.particleController.shoot(particleX, particleY, speed, delay, damage);
        // }
    }

    keydown = (e) => { 
        if(e.code === "ArrowUp") {
            this.upPressed = true;
        }
        if(e.code === "ArrowDown") {
            this.downPressed = true;
        }
        if(e.code === "ArrowLeft") {
            this.leftPressed = true;
        }
        if(e.code === "ArrowRight") {
            this.rightPressed = true;
        }
        if(e.code === "Space") {
            this.shootPressed = true;
        }
    }
    keyup = (e) => {
        if(e.code === "ArrowUp") {
            this.upPressed = false;
        }
        if(e.code === "ArrowDown") {
            this.downPressed = false;
        }
        if(e.code === "ArrowLeft") {
            this.leftPressed = false;
        }
        if(e.code === "ArrowRight") {
            this.rightPressed = false;
        }
        if(e.code === "Space") {
            this.shootPressed = false;
        }
    }


}