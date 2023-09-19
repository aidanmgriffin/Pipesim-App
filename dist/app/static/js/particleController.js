import Particle from './particle.js';

export default class ParticleController {
    particles = [];
    timerUntilNextParticle = 0;
    constructor(canvas) {
        this.canvas = canvas;
    }

    shoot(x, y, speed, delay, damage) {
        if (this.timerUntilNextParticle <= 0) {
            this.particles.push(new Particle(x, y, 5));
            this.timerUntilNextParticle = 10;
        }

        this.timerUntilNextParticle--;
    }

   

    draw(ctx) {
        this.particles.forEach((particle) => {
            if (this.isParticleOutOfBounds(particle)) {
                console.log("OB")
                const index = this.particles.indexOf(particle);
                this.particles.splice(index, 1);
            }
            particle.draw(ctx);
            console.log(this.particles.length)
        });
    }

    isParticleOutOfBounds(particle) {
            return particle.x >= 500; //this.canvas.width;
        }
}