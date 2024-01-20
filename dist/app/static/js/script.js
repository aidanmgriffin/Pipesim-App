import Root from './root.js';
import ParticleController from './particleController.js';

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

canvas.width = 600;
canvas.height = 600;

const particleController = new ParticleController(canvas);
const root = new Root(canvas.width / 2, canvas.height / 2, particleController);

function gameLoop() {
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    particleController.draw(ctx);
    root.draw(ctx);
}



setInterval(gameLoop, 1000 / 60);