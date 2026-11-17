import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface NeuralOrb3DProps {
  className?: string;
  size?: number;
}

export const NeuralOrb3D: React.FC<NeuralOrb3DProps> = ({
  className = '',
  size = 360,
}) => {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
    camera.position.z = 4.2;

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setSize(size, size);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Root Group for Mouse Tilt
    const rootGroup = new THREE.Group();
    scene.add(rootGroup);

    // 1. Inner Core Glowing Sphere (Icosahedron wireframe)
    const innerGeo = new THREE.IcosahedronGeometry(1.25, 2);
    const innerMat = new THREE.MeshBasicMaterial({
      color: 0x00E59B,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const innerMesh = new THREE.Mesh(innerGeo, innerMat);
    rootGroup.add(innerMesh);

    // 2. Synaptic Particle Nodes on Sphere Vertices
    const posAttribute = innerGeo.getAttribute('position');
    const vertexPointsGeo = new THREE.BufferGeometry();
    vertexPointsGeo.setAttribute('position', posAttribute);

    const pointsMat = new THREE.PointsMaterial({
      color: 0x39FFC0,
      size: 0.08,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });
    const vertexPoints = new THREE.Points(vertexPointsGeo, pointsMat);
    rootGroup.add(vertexPoints);

    // 3. Concentric Orbital Rings (Gimbal rings)
    const ringGroup = new THREE.Group();
    rootGroup.add(ringGroup);

    const createOrbitRing = (radius: number, tube: number, color: number, rotX: number, rotY: number) => {
      const ringGeo = new THREE.TorusGeometry(radius, tube, 16, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity: 0.5,
        wireframe: true,
      });
      const ring = new THREE.Mesh(ringGeo, ringMat);
      ring.rotation.x = rotX;
      ring.rotation.y = rotY;
      return ring;
    };

    const ring1 = createOrbitRing(1.7, 0.015, 0x00E59B, Math.PI / 3, 0);
    const ring2 = createOrbitRing(1.9, 0.012, 0x39FFC0, -Math.PI / 4, Math.PI / 6);
    const ring3 = createOrbitRing(2.1, 0.01, 0x00B981, Math.PI / 2, Math.PI / 3);
    ringGroup.add(ring1);
    ringGroup.add(ring2);
    ringGroup.add(ring3);

    // 4. Floating Orbital Dust Particles
    const dustCount = 120;
    const dustGeo = new THREE.BufferGeometry();
    const dustPositions = new Float32Array(dustCount * 3);

    for (let i = 0; i < dustCount; i++) {
      const radius = 1.8 + Math.random() * 1.2;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);

      dustPositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      dustPositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      dustPositions[i * 3 + 2] = radius * Math.cos(phi);
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPositions, 3));

    const dustMat = new THREE.PointsMaterial({
      color: 0x39FFC0,
      size: 0.045,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
    });
    const dustParticles = new THREE.Points(dustGeo, dustMat);
    rootGroup.add(dustParticles);

    // Mouse Tracking for Smooth Parallax Tilt
    let targetRotX = 0;
    let targetRotY = 0;
    let currentRotX = 0;
    let currentRotY = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      targetRotY = x * 0.45;
      targetRotX = -y * 0.45;
    };

    window.addEventListener('mousemove', handleMouseMove, { passive: true });

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      const delta = clock.getDelta();
      const time = clock.getElapsedTime();

      if (!prefersReducedMotion) {
        // Continuous Rotations
        innerMesh.rotation.y += delta * 0.25;
        innerMesh.rotation.x += delta * 0.15;
        vertexPoints.rotation.y += delta * 0.25;
        vertexPoints.rotation.x += delta * 0.15;

        ring1.rotation.z += delta * 0.35;
        ring2.rotation.z -= delta * 0.28;
        ring3.rotation.z += delta * 0.2;

        dustParticles.rotation.y += delta * 0.12;

        // Subtle Breathing Pulse
        const scale = 1 + Math.sin(time * 1.8) * 0.035;
        innerMesh.scale.set(scale, scale, scale);
        vertexPoints.scale.set(scale, scale, scale);
      }

      // Smooth Mouse Interpolation
      currentRotX += (targetRotX - currentRotX) * 0.06;
      currentRotY += (targetRotY - currentRotY) * 0.06;
      rootGroup.rotation.x = currentRotX;
      rootGroup.rotation.y = currentRotY;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', handleMouseMove);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      innerGeo.dispose();
      innerMat.dispose();
      vertexPointsGeo.dispose();
      pointsMat.dispose();
      dustGeo.dispose();
      dustMat.dispose();
      renderer.dispose();
    };
  }, [size]);

  return (
    <div
      ref={mountRef}
      className={`relative flex items-center justify-center select-none ${className}`}
      style={{ width: size, height: size }}
    />
  );
};

