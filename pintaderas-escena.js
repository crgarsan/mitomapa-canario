import {
  DirectionalLight, HemisphereLight, MathUtils, Mesh, MeshStandardMaterial,
  PerspectiveCamera, Scene, Vector3, WebGLRenderer
} from './assets/pintaderas-3d/lib/three.module.js';
import { OrbitControls } from './assets/pintaderas-3d/lib/OrbitControls.js';
import { STLLoader } from './assets/pintaderas-3d/lib/STLLoader.js';

const VISTAS = {
  perspectiva: [0.66, 1.46, 0.96],
  cara: [0, 1, 0.0001],
  perfil: [0, 0, 1],
  reverso: [0, -1, 0.0001]
};

export async function createPintaderaScene(container, url, signal, { color = 0xb46846 } = {}) {
  const response = await fetch(url, { signal });
  if (!response.ok) throw new Error(`No se pudo cargar la pieza (${response.status}).`);
  const buffer = await response.arrayBuffer();
  signal?.throwIfAborted();

  const geometry = new STLLoader().parse(buffer);
  // El STL está en milímetros, con el relieve en +Z. El visor trabaja con +Y arriba.
  geometry.rotateX(-Math.PI / 2);
  geometry.center();
  geometry.computeBoundingSphere();
  const radius = geometry.boundingSphere.radius;
  if (!Number.isFinite(radius) || radius <= 0) {
    geometry.dispose();
    throw new Error('La pieza no tiene una geometría válida.');
  }

  const material = new MeshStandardMaterial({ color, roughness: 0.87 });
  const scene = new Scene();
  scene.add(new Mesh(geometry, material));
  scene.add(new HemisphereLight(0xfff7ec, 0xc8ab98, 1.7));
  const mainLight = new DirectionalLight(0xfff3dd, 2.5);
  mainLight.position.set(-2, 3, -1);
  const fillLight = new DirectionalLight(0xfff1e2, 0.85);
  fillLight.position.set(2, -1, 2);
  scene.add(mainLight, fillLight);

  const camera = new PerspectiveCamera(34, 1, radius / 100, radius * 80);
  const direction = new Vector3();
  let renderer;
  let controls;
  let resizeObserver;
  let frame = 0;
  let lastFrame;
  let fitDistance = 0;
  let disposed = false;

  function requestRender() {
    if (!frame && !disposed) frame = requestAnimationFrame(draw);
  }

  function draw(now) {
    frame = 0;
    if (controls.autoRotate) {
      const delta = lastFrame === undefined ? 0 : Math.min((now - lastFrame) / 1000, 0.05);
      lastFrame = now;
      controls.update(delta);
      requestRender();
    }
    renderer.render(scene, camera);
  }

  function resize() {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    const zoomRatio = fitDistance ? controls.getDistance() / fitDistance : 1;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    const verticalHalf = MathUtils.degToRad(camera.fov / 2);
    const horizontalHalf = Math.atan(Math.tan(verticalHalf) * camera.aspect);
    fitDistance = 1.08 * radius / Math.sin(Math.min(verticalHalf, horizontalHalf));
    controls.minDistance = radius * 1.02;
    controls.maxDistance = fitDistance * 3;
    direction.copy(camera.position).sub(controls.target).normalize();
    const distance = MathUtils.clamp(fitDistance * zoomRatio, controls.minDistance, controls.maxDistance);
    camera.position.copy(controls.target).addScaledVector(direction, distance);
    controls.update(0);
    renderer.setSize(width, height, false);
  }

  function setView(view) {
    if (disposed || !Object.hasOwn(VISTAS, view)) return;
    controls.target.set(0, 0, 0);
    camera.position.fromArray(VISTAS[view]).setLength(fitDistance);
    controls.update(0);
    requestRender();
  }

  function rotate(horizontal, vertical) {
    if (disposed) return;
    if (horizontal) controls.rotateLeft(MathUtils.degToRad(horizontal));
    if (vertical) controls.rotateUp(MathUtils.degToRad(-vertical));
  }

  function zoom(factor) {
    if (!disposed && Number.isFinite(factor) && factor > 0) controls.dollyIn(1 / factor);
  }

  function setAutoRotate(enabled) {
    if (disposed) return;
    controls.autoRotate = Boolean(enabled);
    lastFrame = undefined;
    requestRender();
  }

  function destroy() {
    if (disposed) return;
    disposed = true;
    signal?.removeEventListener('abort', destroy);
    cancelAnimationFrame(frame);
    resizeObserver?.disconnect();
    controls?.removeEventListener('change', requestRender);
    controls?.dispose();
    geometry.dispose();
    material.dispose();
    if (renderer) {
      renderer.dispose();
      if (!renderer.getContext().isContextLost()) renderer.forceContextLoss();
      renderer.domElement.remove();
    }
  }

  try {
    renderer = new WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    const canvas = renderer.domElement;
    canvas.setAttribute('aria-hidden', 'true');
    canvas.style.display = 'block';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.addEventListener('webglcontextlost', () => {
      if (disposed) return;
      destroy();
      container.dispatchEvent(new Event('pintadera-webgl-lost'));
    }, { once: true });
    container.append(canvas);

    camera.position.fromArray(VISTAS.perspectiva);
    controls = new OrbitControls(camera, canvas);
    controls.cursorStyle = 'grab';
    controls.maxTargetRadius = radius * 0.75;
    controls.autoRotateSpeed = 0.8;
    resize();
    setView('perspectiva');
    cancelAnimationFrame(frame);
    draw(performance.now());
    controls.addEventListener('change', requestRender);
    resizeObserver = new ResizeObserver(() => {
      resize();
      requestRender();
    });
    resizeObserver.observe(container);
    signal?.addEventListener('abort', destroy, { once: true });
  } catch (error) {
    destroy();
    throw error;
  }

  return { setView, rotate, zoom, setAutoRotate, destroy };
}
