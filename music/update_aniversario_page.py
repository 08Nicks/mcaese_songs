# -*- coding: utf-8 -*-
"""
Script to build the definitive, clean, beautiful aniversario.html
with pure UTF-8 encoding, organized lyric sections & stanzas,
custom captions for recent photos (Pizza moment & Gorrito rosa),
fixed lightbox polaroid card so caption is rendered INSIDE the card paper,
no duplicate photos, and zero mention of Suno/AI.
"""

html_content = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <meta name="color-scheme" content="dark" />
  <meta name="theme-color" content="#07060b" />
  <title>Feliz Aniversario, Popi ❤️ — De un «Veremos» a Dos Años</title>
  <meta name="description" content="Feliz aniversario Popi, sé que no es mucho pero quise recordarlo. De un «veremos» a dos años juntos... esta canción es para ti." />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Sora:wght@300;400;500;600;700&display=swap" rel="stylesheet" />

  <style>
    :root {
      --bg: #07060b;
      --card: #130f1e;
      --card-inner: #0d0a15;
      --pink: #ff3d81;
      --pink-soft: #ff7aa8;
      --gold: #ffb020;
      --gold-light: #ffd666;
      --wine: #6e163c;
      --text: #f7f2ff;
      --muted: #b5a9cc;
      --faint: #7a708e;
      --line: rgba(255, 255, 255, 0.10);
      --polaroid-bg: #faf7f2;
      --polaroid-text: #241d2d;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }

    body {
      margin: 0;
      min-height: 100vh;
      background-color: var(--bg);
      color: var(--text);
      font-family: "Sora", system-ui, -apple-system, sans-serif;
      overflow-x: hidden;
      position: relative;
    }

    /* -------------------------------------------------------------
       Fondo Ambiental y Partículas Románticas
       ------------------------------------------------------------- */
    .ambient-backdrop {
      position: fixed;
      inset: 0;
      z-index: 0;
      overflow: hidden;
      pointer-events: none;
    }

    .ambient-slide {
      position: absolute;
      inset: -20px;
      background-size: cover;
      background-position: center;
      filter: blur(28px) brightness(0.24) saturate(1.4);
      opacity: 0;
      transition: opacity 2.5s ease-in-out, transform 12s ease-out;
      transform: scale(1.04);
    }
    .ambient-slide.active {
      opacity: 1;
      transform: scale(1.12);
    }

    .ambient-vignette {
      position: absolute;
      inset: 0;
      background:
        radial-gradient(ellipse at 50% 15%, rgba(255, 61, 129, 0.14), transparent 60%),
        radial-gradient(ellipse at 85% 85%, rgba(255, 176, 32, 0.12), transparent 55%),
        linear-gradient(180deg, rgba(7, 6, 11, 0.65) 0%, rgba(7, 6, 11, 0.92) 80%, #07060b 100%);
    }

    /* Corazones flotantes suaves */
    .hearts-layer {
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }
    .floating-heart {
      position: absolute;
      bottom: -40px;
      color: rgba(255, 61, 129, 0.35);
      font-size: 1.2rem;
      user-select: none;
      animation: floatUp 14s linear infinite;
    }
    @keyframes floatUp {
      0% {
        transform: translateY(0) scale(0.8) rotate(0deg);
        opacity: 0;
      }
      10% { opacity: 0.6; }
      90% { opacity: 0.6; }
      100% {
        transform: translateY(-110vh) scale(1.2) rotate(35deg);
        opacity: 0;
      }
    }

    /* -------------------------------------------------------------
       Estructura Principal (Grid 3 columnas en Desktop)
       ------------------------------------------------------------- */
    .page-wrapper {
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: grid;
      grid-template-columns: minmax(220px, 280px) minmax(320px, 780px) minmax(220px, 280px);
      gap: 20px;
      padding: 30px 24px 60px;
      max-width: 1480px;
      margin: 0 auto;
      align-items: start;
    }

    @media (max-width: 1200px) {
      .page-wrapper {
        grid-template-columns: 240px 1fr;
      }
      .photo-sidebar:last-of-type {
        display: none;
      }
    }

    @media (max-width: 960px) {
      .page-wrapper {
        grid-template-columns: 1fr;
        padding: 16px 14px 50px;
        gap: 16px;
      }
      .photo-sidebar {
        display: none !important;
      }
    }

    /* -------------------------------------------------------------
       Sidebars de Fotos Polaroid Flotantes (Desktop)
       ------------------------------------------------------------- */
    .photo-sidebar {
      display: flex;
      flex-direction: column;
      gap: 24px;
      padding-top: 20px;
      position: sticky;
      top: 20px;
    }

    .polaroid {
      background: var(--polaroid-bg);
      color: var(--polaroid-text);
      padding: 10px 10px 16px;
      border-radius: 4px;
      box-shadow:
        0 14px 30px rgba(0, 0, 0, 0.45),
        0 2px 8px rgba(0, 0, 0, 0.25),
        inset 0 0 0 1px rgba(0, 0, 0, 0.06);
      transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease;
      cursor: pointer;
      position: relative;
    }
    .polaroid:hover {
      transform: scale(1.05) rotate(0deg) !important;
      box-shadow:
        0 20px 45px rgba(255, 61, 129, 0.3),
        0 6px 16px rgba(0, 0, 0, 0.4);
      z-index: 10;
    }

    /* Cinta adhesiva decorativa Washi Tape */
    .polaroid::before {
      content: "";
      position: absolute;
      top: -10px;
      left: 50%;
      transform: translateX(-50%);
      width: 55px;
      height: 18px;
      background: rgba(255, 230, 160, 0.7);
      backdrop-filter: blur(2px);
      box-shadow: 0 1px 3px rgba(0,0,0,0.18);
      border-left: 2px dashed rgba(0,0,0,0.15);
      border-right: 2px dashed rgba(0,0,0,0.15);
      z-index: 2;
    }

    .polaroid-img-wrap {
      width: 100%;
      aspect-ratio: 1 / 1;
      overflow: hidden;
      border-radius: 2px;
      background: #1a1622;
    }
    .polaroid-img-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.4s ease;
    }
    .polaroid:hover .polaroid-img-wrap img {
      transform: scale(1.04);
    }

    .polaroid-caption {
      margin: 10px 4px 0;
      text-align: center;
      font-family: "Caveat", cursive;
      font-size: 1.15rem;
      font-weight: 700;
      color: #3b2f4a;
      line-height: 1.2;
    }

    /* Inclinaciones aleatorias para realismo Polaroid */
    .tilt-left-1 { transform: rotate(-3.5deg); }
    .tilt-right-1 { transform: rotate(3deg); }
    .tilt-left-2 { transform: rotate(-2deg); }
    .tilt-right-2 { transform: rotate(4.2deg); }
    .tilt-left-3 { transform: rotate(-4.5deg); }
    .tilt-right-3 { transform: rotate(2.5deg); }

    /* -------------------------------------------------------------
       Carrusel Horizontal de Recuerdos (Móviles)
       ------------------------------------------------------------- */
    .mobile-reel-wrap {
      display: none;
      margin-bottom: 24px;
    }
    @media (max-width: 960px) {
      .mobile-reel-wrap {
        display: block;
      }
    }
    .mobile-reel-title {
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--pink-soft);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin: 0 0 12px 6px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .mobile-reel-title span {
      font-size: 0.72rem;
      color: var(--faint);
      text-transform: none;
      font-weight: 400;
    }

    .mobile-reel {
      display: flex;
      gap: 14px;
      overflow-x: auto;
      padding: 12px 6px 18px;
      scroll-snap-type: x mandatory;
      scrollbar-width: thin;
      scrollbar-color: rgba(255, 61, 129, 0.4) transparent;
      -webkit-overflow-scrolling: touch;
    }
    .mobile-reel::-webkit-scrollbar { height: 6px; }
    .mobile-reel::-webkit-scrollbar-thumb {
      background: rgba(255, 61, 129, 0.4);
      border-radius: 99px;
    }
    .mobile-reel .polaroid {
      flex: 0 0 180px;
      scroll-snap-align: start;
    }
    .mobile-reel .polaroid .polaroid-caption {
      font-size: 1rem;
    }

    /* -------------------------------------------------------------
       Columna Central: Contenedor Romántico
       ------------------------------------------------------------- */
    .center-content {
      display: flex;
      flex-direction: column;
      gap: 22px;
    }

    /* Hero / Encabezado */
    .anniversary-hero {
      background:
        radial-gradient(ellipse at 80% 0%, rgba(255, 61, 129, 0.18), transparent 60%),
        radial-gradient(ellipse at 10% 100%, rgba(255, 176, 32, 0.15), transparent 60%),
        linear-gradient(145deg, rgba(23, 17, 36, 0.85), rgba(13, 10, 21, 0.95));
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 32px 28px 26px;
      text-align: center;
      box-shadow:
        0 24px 60px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.12);
      backdrop-filter: blur(14px);
    }

    .love-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 61, 129, 0.15);
      border: 1px solid rgba(255, 61, 129, 0.35);
      border-radius: 999px;
      padding: 6px 16px;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--pink-soft);
      margin-bottom: 14px;
    }
    .love-pill span { font-size: 1rem; }

    .anniversary-title {
      font-family: "Playfair Display", Georgia, serif;
      font-size: clamp(2rem, 5vw, 2.9rem);
      font-weight: 700;
      margin: 0 0 12px;
      background: linear-gradient(135deg, #ffffff 30%, #ffd666 70%, #ff7aa8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1.18;
    }

    .anniversary-dedication {
      font-family: "Caveat", cursive;
      font-size: clamp(1.35rem, 3.4vw, 1.7rem);
      color: #f0e6ff;
      margin: 0 auto 16px;
      max-width: 620px;
      line-height: 1.35;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    }
    .anniversary-dedication strong {
      color: var(--gold-light);
    }

    .song-credits {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--muted);
      background: rgba(255, 255, 255, 0.04);
      padding: 6px 14px;
      border-radius: 999px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* -------------------------------------------------------------
       Reproductor de Audio Estilo Tarjeta
       ------------------------------------------------------------- */
    .player-card {
      background: linear-gradient(160deg, rgba(23, 18, 35, 0.9), rgba(15, 11, 23, 0.95));
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 22px 24px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(12px);
    }

    .player-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }
    .player-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--pink-soft);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .player-badge .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--pink);
      box-shadow: 0 0 10px var(--pink);
      animation: pulseDot 2s infinite ease-in-out;
    }
    @keyframes pulseDot {
      0%, 100% { opacity: 0.5; transform: scale(0.9); }
      50% { opacity: 1; transform: scale(1.15); }
    }

    audio {
      width: 100%;
      height: 48px;
      border-radius: 12px;
      outline: none;
      filter: drop-shadow(0 4px 14px rgba(0, 0, 0, 0.4));
    }

    /* -------------------------------------------------------------
       Tarjeta de Letra Sincronizada (Karaoke Estilo Spotify/Poema)
       ------------------------------------------------------------- */
    .karaoke-card {
      background: linear-gradient(165deg, rgba(20, 15, 32, 0.92), rgba(12, 9, 19, 0.96));
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 26px 28px;
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(14px);
      position: relative;
    }

    .karaoke-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 14px;
    }
    .kicker {
      font-size: 0.72rem;
      font-weight: 800;
      color: var(--gold);
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin: 0 0 4px;
    }
    .section-title {
      margin: 0;
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* Contenedor scrolleable de letra */
    .lyrics-container {
      max-height: 480px;
      overflow-y: auto;
      padding: 10px 8px 30px;
      scroll-behavior: smooth;
      scrollbar-width: thin;
      scrollbar-color: rgba(255, 61, 129, 0.4) transparent;
      user-select: text;
    }
    .lyrics-container::-webkit-scrollbar { width: 5px; }
    .lyrics-container::-webkit-scrollbar-thumb {
      background: rgba(255, 61, 129, 0.35);
      border-radius: 99px;
    }

    /* Encabezados y bloques organizados de secciones */
    .lyrics-section-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 30px 0 14px 0;
      padding-top: 8px;
      user-select: none;
    }
    .lyrics-section-header:first-of-type {
      margin-top: 4px;
      padding-top: 0;
    }
    .section-tag-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      font-weight: 800;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #ffd666;
      background: rgba(255, 214, 102, 0.12);
      border: 1px solid rgba(255, 214, 102, 0.35);
      padding: 4px 14px;
      border-radius: 999px;
      box-shadow: 0 0 16px rgba(255, 214, 102, 0.15);
      transition: all 0.3s ease;
    }
    .lyrics-section-header.is-active-section .section-tag-badge {
      background: rgba(255, 214, 102, 0.28);
      border-color: #ffd666;
      color: #fff;
      box-shadow: 0 0 22px rgba(255, 214, 102, 0.45);
      transform: scale(1.04);
    }
    .section-tag-line {
      flex: 1;
      height: 1px;
      background: linear-gradient(90deg, rgba(255, 214, 102, 0.3), transparent);
    }

    .lyrics-section-block {
      margin-bottom: 24px;
      padding-left: 16px;
      border-left: 2px solid rgba(255, 255, 255, 0.08);
      border-radius: 0 10px 10px 0;
      transition: border-color 0.3s ease, background 0.3s ease;
    }
    .lyrics-section-block.is-active-section {
      border-left-color: rgba(255, 214, 102, 0.75);
      background: linear-gradient(90deg, rgba(255, 214, 102, 0.05), transparent 70%);
    }

    .line {
      margin: 0 0 12px;
      font-size: clamp(1.02rem, 3.1vw, 1.22rem);
      line-height: 1.62;
      color: #7b7194;
      transition: color 0.25s ease, transform 0.25s ease;
      cursor: pointer;
    }
    .line.is-stanza-end {
      margin-bottom: 24px; /* Separación limpia entre estrofas */
    }
    .line:hover {
      color: #b5a9d2;
    }
    .line.active {
      color: #ffffff;
      transform: translateX(4px);
    }

    /* Palabras iluminadas en sincronía */
    .word {
      display: inline-block;
      padding: 0 2px;
      border-radius: 4px;
      transition: color 0.12s ease, text-shadow 0.12s ease;
    }
    .line.active .word {
      color: #9c91b5;
    }
    .line.active .word.active {
      color: #ffd666;
      font-weight: 700;
      text-shadow:
        0 0 18px rgba(255, 176, 32, 0.75),
        0 0 32px rgba(255, 61, 129, 0.5);
      animation: popWord 0.15s ease-out;
    }
    @keyframes popWord {
      0% { transform: scale(1.08); }
      100% { transform: scale(1); }
    }

    /* -------------------------------------------------------------
       Pie de Página con Descarga y Nota Romántica
       ------------------------------------------------------------- */
    .romantic-footer {
      text-align: center;
      padding: 24px 16px;
      border-top: 1px solid var(--line);
      margin-top: 24px;
    }
    .download-cta {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: linear-gradient(135deg, #ffd36b, #ff3d81);
      color: #120e1c;
      font-weight: 800;
      font-size: 0.95rem;
      padding: 13px 26px;
      border-radius: 999px;
      text-decoration: none;
      box-shadow: 0 10px 30px rgba(255, 61, 129, 0.4);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      margin-bottom: 12px;
    }
    .download-cta:hover {
      transform: translateY(-2px);
      box-shadow: 0 14px 40px rgba(255, 61, 129, 0.55);
    }
    .footer-note {
      font-size: 0.88rem;
      color: var(--faint);
      margin: 14px 0 0;
    }
    .footer-note strong {
      color: var(--pink-soft);
    }

    /* -------------------------------------------------------------
       Modal Lightbox para Fotos en Grande (Diseño Polaroid Auténtico)
       ------------------------------------------------------------- */
    .lightbox-modal {
      position: fixed;
      inset: 0;
      z-index: 9999;
      background: rgba(7, 6, 11, 0.94);
      backdrop-filter: blur(18px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .lightbox-modal.is-open {
      display: flex;
      opacity: 1;
    }
    .lightbox-card {
      background: var(--polaroid-bg);
      color: var(--polaroid-text);
      padding: 14px 14px 22px;
      border-radius: 8px;
      box-shadow:
        0 25px 80px rgba(0, 0, 0, 0.8),
        0 0 0 1px rgba(255, 255, 255, 0.12);
      max-width: min(92vw, 640px);
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      position: relative;
      animation: modalZoom 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
    }
    @keyframes modalZoom {
      0% { transform: scale(0.85); opacity: 0; }
      100% { transform: scale(1); opacity: 1; }
    }
    .lightbox-card::before {
      content: "";
      position: absolute;
      top: -12px;
      left: 50%;
      transform: translateX(-50%);
      width: 70px;
      height: 22px;
      background: rgba(255, 230, 160, 0.85);
      backdrop-filter: blur(2px);
      box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      border-left: 3px dashed rgba(0,0,0,0.18);
      border-right: 3px dashed rgba(0,0,0,0.18);
      z-index: 2;
    }
    .lightbox-img-wrap {
      width: 100%;
      max-height: 70vh;
      overflow: hidden;
      border-radius: 4px;
      background: #140f1e;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .lightbox-img-wrap img {
      max-width: 100%;
      max-height: 70vh;
      width: auto;
      height: auto;
      object-fit: contain;
      display: block;
      border-radius: 2px;
    }
    .lightbox-caption-text {
      margin: 14px 10px 4px;
      text-align: center;
      font-family: "Caveat", cursive;
      font-size: clamp(1.4rem, 4.2vw, 1.85rem);
      font-weight: 700;
      color: #241d2d;
      line-height: 1.25;
      text-shadow: 0 1px 1px rgba(0,0,0,0.08);
    }
    .lightbox-caption-text:empty {
      display: none;
    }
    .lightbox-close-btn {
      position: absolute;
      top: 24px;
      right: 24px;
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      font-size: 1.4rem;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
    }
    .lightbox-close-btn:hover { background: rgba(255, 61, 129, 0.4); }
  </style>
</head>
<body>

  <!-- Fondo Ambiental con Fotos y Corazones -->
  <div class="ambient-backdrop" aria-hidden="true">
    <div class="ambient-slide active" id="ambientSlideA" style="background-image: url('fotos/IMG-20261108-WA0225.jpg');"></div>
    <div class="ambient-slide" id="ambientSlideB"></div>
    <div class="ambient-vignette"></div>
    <div class="hearts-layer" id="heartsLayer"></div>
  </div>

  <div class="page-wrapper">

    <!-- =========================================================
         COLUMNA IZQUIERDA: POLAROIDS FLOTANTES (DESKTOP)
         ========================================================= -->
    <aside class="photo-sidebar" aria-label="Fotos de recuerdos - Izquierda">
      <div class="polaroid tilt-left-1" onclick="openLightbox('fotos/reciente-01.jpg', 'Pizza moment 🍕✨')">
        <div class="polaroid-img-wrap">
          <img src="fotos/reciente-01.jpg" alt="Pizza moment con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Pizza moment 🍕</p>
      </div>

      <div class="polaroid tilt-right-1" onclick="openLightbox('fotos/reciente-02.jpg', 'Juntos siempre ❤️')">
        <div class="polaroid-img-wrap">
          <img src="fotos/reciente-02.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Juntos siempre ❤️</p>
      </div>

      <div class="polaroid tilt-left-2" onclick="openLightbox('fotos/IMG-20260609-WA0116.jpg', 'Nuestras sonrisas')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20260609-WA0116.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Nuestras sonrisas</p>
      </div>

      <div class="polaroid tilt-right-2" onclick="openLightbox('fotos/IMG-20260921-WA0125.jpg', 'Siempre juntos')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20260921-WA0125.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Siempre juntos</p>
      </div>

      <div class="polaroid tilt-left-3" onclick="openLightbox('fotos/IMG-20261020-WA0071.jpg', 'Donde sea, pero contigo')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20261020-WA0071.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Donde sea, pero contigo</p>
      </div>

      <div class="polaroid tilt-right-3" onclick="openLightbox('fotos/IMG-20261108-WA0222.jpg', 'Dos años de amor')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20261108-WA0222.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Dos años de amor</p>
      </div>
    </aside>

    <!-- =========================================================
         COLUMNA CENTRAL: DEDICATORIA + REPRODUCTOR + KARAOKE
         ========================================================= -->
    <main class="center-content">

      <!-- Encabezado Romántico -->
      <header class="anniversary-hero">
        <div class="love-pill">
          <span>❤️</span> 2 Años Juntos · Aniversario
        </div>

        <h1 class="anniversary-title">Feliz Aniversario, Popi</h1>

        <p class="anniversary-dedication">
          «Sé que no es mucho, pero quise recordarlo… de un <strong>«a ver qué pasa»</strong> a dos años sin soltarnos la mano.»
        </p>

        <div class="song-credits">
          🎵 Canción: <b>De un «Veremos» a Dos Años</b>
        </div>
      </header>

      <!-- Carrusel Horizontal para Celulares -->
      <section class="mobile-reel-wrap" aria-label="Galería de fotos de aniversario">
        <p class="mobile-reel-title">📸 Nuestros Recuerdos <span>(Toca para agrandar)</span></p>
        <div class="mobile-reel">
          <div class="polaroid tilt-left-1" onclick="openLightbox('fotos/reciente-01.jpg', 'Pizza moment 🍕✨')">
            <div class="polaroid-img-wrap"><img src="fotos/reciente-01.jpg" alt="Pizza moment" loading="lazy" /></div>
            <p class="polaroid-caption">Pizza moment 🍕</p>
          </div>
          <div class="polaroid tilt-right-1" onclick="openLightbox('fotos/reciente-02.jpg', 'Juntos siempre ❤️')">
            <div class="polaroid-img-wrap"><img src="fotos/reciente-02.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Juntos ❤️</p>
          </div>
          <div class="polaroid tilt-left-2" onclick="openLightbox('fotos/reciente-03.jpg', 'Ese gorrito rosa que tanto amo 🌸💕')">
            <div class="polaroid-img-wrap"><img src="fotos/reciente-03.jpg" alt="Tu gorrito rosa" loading="lazy" /></div>
            <p class="polaroid-caption">Tu gorrito rosa 🌸</p>
          </div>
          <div class="polaroid tilt-left-3" onclick="openLightbox('fotos/IMG-20260609-WA0094.jpg', 'De un «veremos»…')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20260609-WA0094.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">De un «veremos»…</p>
          </div>
          <div class="polaroid tilt-right-1" onclick="openLightbox('fotos/IMG-20260609-WA0116.jpg', 'Nuestras sonrisas')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20260609-WA0116.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Sonrisas</p>
          </div>
          <div class="polaroid tilt-left-1" onclick="openLightbox('fotos/IMG-20260921-WA0125.jpg', 'Siempre juntos')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20260921-WA0125.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Siempre juntos</p>
          </div>
          <div class="polaroid tilt-right-2" onclick="openLightbox('fotos/IMG-20260921-WA0129.jpg', 'A no soltarnos la mano')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20260921-WA0129.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">A no soltarnos…</p>
          </div>
          <div class="polaroid tilt-left-2" onclick="openLightbox('fotos/IMG-20261020-WA0071.jpg', 'Donde sea, pero contigo')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20261020-WA0071.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Conectados</p>
          </div>
          <div class="polaroid tilt-right-3" onclick="openLightbox('fotos/IMG-20261108-WA0222.jpg', 'Dos años de amor')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20261108-WA0222.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Dos años</p>
          </div>
          <div class="polaroid tilt-left-1" onclick="openLightbox('fotos/IMG-20261108-WA0223(1).jpg', 'Mi lugar favorito')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20261108-WA0223(1).jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Mi lugar favorito</p>
          </div>
          <div class="polaroid tilt-right-1" onclick="openLightbox('fotos/IMG-20261108-WA0224(2).jpg', 'Tú en cada plano')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20261108-WA0224(2).jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">En cada plano</p>
          </div>
          <div class="polaroid tilt-right-3" onclick="openLightbox('fotos/IMG-20261108-WA0225.jpg', 'Por muchos años más, Popi ❤️')">
            <div class="polaroid-img-wrap"><img src="fotos/IMG-20261108-WA0225.jpg" alt="Recuerdo" loading="lazy" /></div>
            <p class="polaroid-caption">Por muchos más ❤️</p>
          </div>
        </div>
      </section>

      <!-- Reproductor de Audio -->
      <section class="player-card">
        <!-- 1. Canción Principal (Versión Estudio) -->
        <div class="player-header">
          <div class="player-badge">
            <span class="dot"></span>
            <span>🎵 Nuestra Canción (Versión Estudio)</span>
          </div>
          <span style="font-size: 0.8rem; color: var(--faint);">5:03 min</span>
        </div>

        <audio id="audio" controls preload="metadata" src="music/de-un-veremos-a-dos-anos-estudio.mp3">
          Tu navegador no soporta el reproductor de audio.
        </audio>

        <!-- Divisor elegante -->
        <div style="height: 1px; background: var(--line); margin: 20px 0 16px;"></div>

        <!-- 2. Versión con mi voz -->
        <div class="player-header">
          <div class="player-badge" style="color: var(--gold-light);">
            <span class="dot" style="background: var(--gold); box-shadow: 0 0 10px var(--gold);"></span>
            <span>🎙️ Versión con mi voz (Josué para Popi)</span>
          </div>
          <span style="font-size: 0.8rem; color: var(--faint);">7:23 min</span>
        </div>

        <audio id="audioVoz" controls preload="metadata" src="music/de-un-veremos-a-dos-anos-mezcla.mp3">
          Tu navegador no soporta el reproductor de audio.
        </audio>
      </section>

      <!-- Letra en Tiempo Real Organizada en Secciones (Karaoke) -->
      <section class="karaoke-card">
        <div class="karaoke-head">
          <div>
            <p class="kicker">Letra & Poesía Sincronizada</p>
            <h2 id="sectionName" class="section-title">Intro</h2>
          </div>
          <span id="timeLabel" style="font-size: 0.82rem; color: var(--faint); font-variant-numeric: tabular-nums;">0:00 / 5:03</span>
        </div>

        <div class="lyrics-container" id="lyricsContainer">
          <div id="lyrics">Cargando letra sincronizada…</div>
        </div>
      </section>

      <!-- Pie con Descarga y Mensaje -->
      <footer class="romantic-footer">
        <div style="display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
          <a class="download-cta" href="music/de-un-veremos-a-dos-anos-estudio.mp3" download="De Un Veremos a Dos Anos - Popi (Estudio).mp3">
            🎵 Descargar Versión Estudio (MP3)
          </a>
          <a class="download-cta" href="music/de-un-veremos-a-dos-anos-mezcla.mp3" download="De Un Veremos a Dos Anos - Popi (Con mi voz).mp3" style="background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.2); color: #fff;">
            🎙️ Descargar Versión con mi Voz (MP3)
          </a>
        </div>
        <p class="footer-note" style="margin-top: 18px;">
          Hecho con todo el corazón para <strong>Popi</strong> · Puebla y CDMX · <strong>2 Años Juntos</strong> ❤️
        </p>
      </footer>

    </main>

    <!-- =========================================================
         COLUMNA DERECHA: POLAROIDS FLOTANTES (DESKTOP)
         ========================================================= -->
    <aside class="photo-sidebar" aria-label="Fotos de recuerdos - Derecha">
      <div class="polaroid tilt-right-1" onclick="openLightbox('fotos/reciente-03.jpg', 'Ese gorrito rosa que tanto amo 🌸💕')">
        <div class="polaroid-img-wrap">
          <img src="fotos/reciente-03.jpg" alt="Tu gorrito rosa" loading="lazy" />
        </div>
        <p class="polaroid-caption">Tu gorrito rosa 🌸</p>
      </div>

      <div class="polaroid tilt-left-1" onclick="openLightbox('fotos/IMG-20260609-WA0094.jpg', 'De un «veremos»…')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20260609-WA0094.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">De un «veremos»…</p>
      </div>

      <div class="polaroid tilt-right-2" onclick="openLightbox('fotos/IMG-20260921-WA0129.jpg', 'A no soltarnos la mano')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20260921-WA0129.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">A no soltarnos la mano</p>
      </div>

      <div class="polaroid tilt-left-2" onclick="openLightbox('fotos/IMG-20261108-WA0223(1).jpg', 'Mi lugar favorito en el mundo')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20261108-WA0223(1).jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Mi lugar favorito</p>
      </div>

      <div class="polaroid tilt-right-2" onclick="openLightbox('fotos/IMG-20261108-WA0224(2).jpg', 'Tú en cada plano')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20261108-WA0224(2).jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Tú en cada plano</p>
      </div>

      <div class="polaroid tilt-right-3" onclick="openLightbox('fotos/IMG-20261108-WA0225.jpg', 'Por muchos años más, Popi ❤️')">
        <div class="polaroid-img-wrap">
          <img src="fotos/IMG-20261108-WA0225.jpg" alt="Recuerdo con Popi" loading="lazy" />
        </div>
        <p class="polaroid-caption">Por muchos años más ❤️</p>
      </div>
    </aside>

  </div>

  <!-- Modal Lightbox (Diseño Polaroid Auténtico) -->
  <div id="lightbox" class="lightbox-modal" onclick="closeLightbox(event)">
    <button class="lightbox-close-btn" onclick="closeLightbox(event)" aria-label="Cerrar foto">✕</button>
    <div class="lightbox-card" onclick="event.stopPropagation()">
      <div class="lightbox-img-wrap">
        <img id="lightboxImg" src="" alt="Foto ampliada" />
      </div>
      <p id="lightboxCaption" class="lightbox-caption-text"></p>
    </div>
  </div>

  <!-- Datos y Lógica de Karaoke -->
  <script src="music/karaoke-data.js"></script>
  <script>
    (() => {
      "use strict";

      const data = window.KARAOKE_DATA;
      const audio = document.getElementById("audio");
      const audioVoz = document.getElementById("audioVoz");
      const lyricsEl = document.getElementById("lyrics");
      const lyricsContainer = document.getElementById("lyricsContainer");
      const sectionNameEl = document.getElementById("sectionName");
      const timeLabel = document.getElementById("timeLabel");

      // Pausa mutua de reproductores
      if (audioVoz) {
        audio.addEventListener("play", () => {
          if (!audioVoz.paused) audioVoz.pause();
        });
        audioVoz.addEventListener("play", () => {
          if (!audio.paused) audio.pause();
        });
      }

      if (!data) {
        lyricsEl.innerHTML = "<p class='line active'>No se pudo cargar la letra.</p>";
        return;
      }

      function fmt(sec) {
        if (!sec || isNaN(sec) || sec < 0) sec = 0;
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${m}:${s.toString().padStart(2, "0")}`;
      }

      function updateTimeLabel() {
        if (!timeLabel) return;
        const dur = audio.duration || data.duration || 303;
        timeLabel.textContent = `${fmt(audio.currentTime)} / ${fmt(dur)}`;
      }

      // -------------------------------------------------------------
      // Renderizado Organizado por Secciones y Estrofas
      // -------------------------------------------------------------
      let lineEls = [];
      let sectionElements = [];

      function renderLyrics() {
        const frag = document.createDocumentFragment();
        lineEls = [];
        sectionElements = [];

        data.sections.forEach((section, sIdx) => {
          // Encabezado visual de Sección: [Intro], [Verso 1], [Coro], etc.
          const secHeader = document.createElement("div");
          secHeader.className = "lyrics-section-header";
          secHeader.dataset.sectionIndex = sIdx;
          secHeader.innerHTML = `
            <span class="section-tag-badge">${section.tag || `[${section.name}]`}</span>
            <span class="section-tag-line"></span>
          `;
          frag.appendChild(secHeader);

          // Contenedor de líneas de la sección
          const secBlock = document.createElement("div");
          secBlock.className = "lyrics-section-block";
          secBlock.dataset.sectionIndex = sIdx;

          section.lines.forEach((line) => {
            const p = document.createElement("p");
            p.className = "line";
            if (line.isLastInStanza) {
              p.classList.add("is-stanza-end");
            }
            p.dataset.start = line.start;
            p.dataset.end = line.end;

            // Al hacer clic en un verso, saltar a ese momento
            p.addEventListener("click", () => {
              audio.currentTime = line.start;
              audio.play().catch(() => {});
            });

            const itemWords = [];
            if (line.words && line.words.length) {
              line.words.forEach((w, i) => {
                const sp = document.createElement("span");
                sp.className = "word";
                sp.textContent = w.text + (i < line.words.length - 1 ? " " : "");
                p.appendChild(sp);
                itemWords.push({ el: sp, word: w });
              });
            } else {
              p.textContent = line.text;
            }

            secBlock.appendChild(p);
            lineEls.push({
              el: p,
              line,
              words: itemWords,
              sectionIndex: sIdx,
              secHeader,
              secBlock
            });
          });

          frag.appendChild(secBlock);
          sectionElements.push({
            header: secHeader,
            block: secBlock,
            section
          });
        });

        lyricsEl.innerHTML = "";
        lyricsEl.appendChild(frag);
      }

      renderLyrics();

      // -------------------------------------------------------------
      // Bucle de Karaoke & Sincronización Fluida
      // -------------------------------------------------------------
      let lastActive = null;
      let lastSecIndex = -1;
      let raf = null;

      function updateKaraoke() {
        const songT = Math.max(0, audio.currentTime);

        // Identificar sección actual
        let currentSectionIdx = 0;
        for (let i = 0; i < data.sections.length; i++) {
          const sec = data.sections[i];
          if (songT >= sec.start && songT < sec.end) {
            currentSectionIdx = i;
            break;
          }
          if (songT >= sec.end) currentSectionIdx = i;
        }

        const curSec = data.sections[currentSectionIdx];
        if (sectionNameEl && curSec) {
          sectionNameEl.textContent = curSec.tag ? curSec.tag.replace(/[\\[\\]]/g, "") : curSec.name;
        }

        // Iluminar la sección activa visualmente
        if (currentSectionIdx !== lastSecIndex) {
          sectionElements.forEach((sObj, idx) => {
            const isCur = idx === currentSectionIdx;
            sObj.header.classList.toggle("is-active-section", isCur);
            sObj.block.classList.toggle("is-active-section", isCur);
          });
          lastSecIndex = currentSectionIdx;
        }

        // Línea actual (la más reciente que ya haya empezado)
        let activeLine = null;
        if (lineEls.length) {
          if (songT < lineEls[0].line.start) {
            activeLine = lineEls[0];
          } else {
            for (let i = lineEls.length - 1; i >= 0; i--) {
              if (songT >= lineEls[i].line.start) {
                const next = lineEls[i + 1];
                if (!next || songT < next.line.start) {
                  activeLine = lineEls[i];
                  break;
                }
              }
            }
          }
        }

        if (activeLine !== lastActive) {
          if (lastActive) {
            lastActive.el.classList.remove("active");
            if (lastActive.words) {
              lastActive.words.forEach(w => w.el.classList.remove("active"));
            }
          }
          if (activeLine) {
            activeLine.el.classList.add("active");
            activeLine.el.scrollIntoView({ block: "center", behavior: "smooth" });
          }
          lastActive = activeLine;
        }

        // Iluminación progresiva continua de palabras en el verso activo
        if (activeLine && activeLine.words) {
          activeLine.words.forEach((wObj) => {
            wObj.el.classList.toggle("active", songT >= wObj.word.start);
          });
        }

        updateTimeLabel();
      }

      function loop() {
        updateKaraoke();
        if (!audio.paused) raf = requestAnimationFrame(loop);
      }

      audio.addEventListener("play", () => {
        cancelAnimationFrame(raf);
        loop();
      });
      audio.addEventListener("pause", () => {
        cancelAnimationFrame(raf);
        updateKaraoke();
      });
      audio.addEventListener("seeked", updateKaraoke);
      audio.addEventListener("timeupdate", updateKaraoke);
      audio.addEventListener("loadedmetadata", updateTimeLabel);

      // -------------------------------------------------------------
      // Fondo Dinámico y Lluvia de Corazones
      // -------------------------------------------------------------
      const allPhotos = [
        "fotos/reciente-01.jpg",
        "fotos/reciente-02.jpg",
        "fotos/reciente-03.jpg",
        "fotos/IMG-20260609-WA0094.jpg",
        "fotos/IMG-20260609-WA0116.jpg",
        "fotos/IMG-20260921-WA0125.jpg",
        "fotos/IMG-20260921-WA0129.jpg",
        "fotos/IMG-20261020-WA0071.jpg",
        "fotos/IMG-20261108-WA0222.jpg",
        "fotos/IMG-20261108-WA0223(1).jpg",
        "fotos/IMG-20261108-WA0224(2).jpg",
        "fotos/IMG-20261108-WA0225.jpg"
      ];

      let bgIndex = 0;
      const slideA = document.getElementById("ambientSlideA");
      const slideB = document.getElementById("ambientSlideB");
      let currentSlide = slideA;

      setInterval(() => {
        bgIndex = (bgIndex + 1) % allPhotos.length;
        const nextPhoto = allPhotos[bgIndex];
        const nextSlide = (currentSlide === slideA) ? slideB : slideA;

        nextSlide.style.backgroundImage = `url('${nextPhoto}')`;
        nextSlide.classList.add("active");
        currentSlide.classList.remove("active");
        currentSlide = nextSlide;
      }, 7000);

      // Crear corazones flotantes de fondo
      const heartsLayer = document.getElementById("heartsLayer");
      const heartSymbols = ["❤️", "💖", "✨", "💕", "🌸"];
      function spawnHeart() {
        const el = document.createElement("div");
        el.className = "floating-heart";
        el.textContent = heartSymbols[Math.floor(Math.random() * heartSymbols.length)];
        el.style.left = `${Math.random() * 100}%`;
        el.style.fontSize = `${0.9 + Math.random() * 0.9}rem`;
        el.style.animationDuration = `${10 + Math.random() * 8}s`;
        heartsLayer.appendChild(el);
        setTimeout(() => el.remove(), 18000);
      }
      setInterval(spawnHeart, 1600);
      for (let i = 0; i < 7; i++) spawnHeart();

    })();

    // -------------------------------------------------------------
    // Funciones del Modal Lightbox
    // -------------------------------------------------------------
    function openLightbox(src, caption) {
      const modal = document.getElementById("lightbox");
      const img = document.getElementById("lightboxImg");
      const cap = document.getElementById("lightboxCaption");
      img.src = src;
      cap.textContent = caption || "";
      modal.classList.add("is-open");
    }

    function closeLightbox(e) {
      if (e) e.stopPropagation();
      document.getElementById("lightbox").classList.remove("is-open");
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeLightbox();
    });
  </script>
</body>
</html>
"""

with open("aniversario.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("SUCCESS: Lightbox polaroid card structure updated with caption inside!")
