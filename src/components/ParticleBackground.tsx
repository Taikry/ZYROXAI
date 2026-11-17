import React, { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  baseAlpha: number;
  alpha: number;
  color: string;
}

interface PulseWave {
  x: number;
  y: number;
  radius: number;
  maxRadius: number;
  alpha: number;
}

export const ParticleBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) return;

    // Check reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const isMobile = width < 768;
    const particleCount = isMobile ? 32 : prefersReducedMotion ? 20 : 68;
    const maxDistance = isMobile ? 80 : 120;

    const particles: Particle[] = [];
    const colors = ['#00E59B', '#39FFC0', '#00B981'];

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * (prefersReducedMotion ? 0.1 : 0.38),
        vy: (Math.random() - 0.5) * (prefersReducedMotion ? 0.1 : 0.38),
        radius: Math.random() * 1.8 + 0.8,
        baseAlpha: Math.random() * 0.35 + 0.15,
        alpha: Math.random() * 0.35 + 0.15,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    let mouseX = -1000;
    let mouseY = -1000;
    const pulseWaves: PulseWave[] = [];

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    const handleClick = (e: MouseEvent) => {
      if (prefersReducedMotion) return;
      pulseWaves.push({
        x: e.clientX,
        y: e.clientY,
        radius: 10,
        maxRadius: isMobile ? 120 : 220,
        alpha: 0.6,
      });
    };

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });
    window.addEventListener('click', handleClick, { passive: true });
    window.addEventListener('resize', handleResize, { passive: true });

    let time = 0;

    const render = () => {
      time += 0.015;
      ctx.clearRect(0, 0, width, height);

      // Draw subtle radial glow behind hero
      const bgGrad = ctx.createRadialGradient(
        width * 0.5,
        height * 0.28,
        50,
        width * 0.5,
        height * 0.28,
        width * 0.55
      );
      bgGrad.addColorStop(0, 'rgba(0, 229, 155, 0.055)');
      bgGrad.addColorStop(0.5, 'rgba(0, 185, 129, 0.018)');
      bgGrad.addColorStop(1, 'rgba(5, 8, 7, 0)');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      // Render & Expand Click Pulse Waves
      for (let i = pulseWaves.length - 1; i >= 0; i--) {
        const wave = pulseWaves[i];
        wave.radius += 3.5;
        wave.alpha *= 0.94;

        ctx.beginPath();
        ctx.arc(wave.x, wave.y, wave.radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(0, 229, 155, ${wave.alpha})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        if (wave.alpha < 0.02 || wave.radius >= wave.maxRadius) {
          pulseWaves.splice(i, 1);
        }
      }

      // Update and Draw Synaptic Particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (!prefersReducedMotion) {
          p.x += p.vx;
          p.y += p.vy;

          // Bounce off viewport bounds
          if (p.x < 0) { p.x = 0; p.vx *= -1; }
          else if (p.x > width) { p.x = width; p.vx *= -1; }
          if (p.y < 0) { p.y = 0; p.vy *= -1; }
          else if (p.y > height) { p.y = height; p.vy *= -1; }

          // Ambient breathing alpha
          p.alpha = p.baseAlpha + Math.sin(time + i) * 0.12;

          // Gentle mouse gravity / repulsion
          const dxMouse = p.x - mouseX;
          const dyMouse = p.y - mouseY;
          const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);

          if (distMouse < 120 && distMouse > 0) {
            const force = (120 - distMouse) / 120;
            p.x += (dxMouse / distMouse) * force * 1.5;
            p.y += (dyMouse / distMouse) * force * 1.5;
          }
        }

        // Draw particle node
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = Math.max(0.06, Math.min(1, p.alpha));
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(57, 255, 192, 0.5)';
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.globalAlpha = 1;

        // Connect adjacent nodes
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < maxDistance) {
            const lineAlpha = (1 - dist / maxDistance) * 0.18;
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(0, 229, 155, ${lineAlpha})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('click', handleClick);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0 opacity-80"
      style={{ willChange: 'transform' }}
    />
  );
};
