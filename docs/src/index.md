---
# https://vitepress.dev/reference/default-theme-home-page
layout: home
pageClass: home

hero:
  name: "💠 Fractalistic"
  text: "The Terminal-Based Fractal Explorer"
  tagline: "Fractalistic is your terminal gateway to Mandelbrot, Burning Ship, and Julia."
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/SkwalExe/fractalistic

features:
  - title: Multi-threaded
    details: Fractalistic leverages parallel processing for complex arithmetic operations, enabling smooth navigation and rapid rendering.
    icon: ⚡
  - title: High Precision Arithmetics
    details: "Using MPFR and GMPY2, Fractalistic allows you to explore fractals infinitely deep by enabling users to increase the decimal precision for calculations as needed."
    icon: 🔢
  - title: High Quality Screenshots
    details: Fractalistic not only allows you to explore fractals at terminal resolution but also lets you generate high-resolution captures of your current view.
    icon: 📸
  - title: Next-gen Terminal User Interface
    details: Fractalistic utilizes modern libraries such as Will McGugan's Textual framework to provide a full-featured navigation experience, all this in your classic terminal. Fractalistic also supports customizable mouse inputs, allowing for seemless navigation.
    icon: ✨
  - title: Robust Command System
    details: "Fractalistic offers a robust command system that goes beyond simple fractal navigation. Additional features include capturing high-definition screenshots, adjusting render settings, modifying navigation preferences, changing colors, and much more."
    icon: 📌
  - title: Modular Rendering Engine
    details: "Fractalistic's underlying rendering engine is highly modular. The integrated command system enables you to inspect and modify technical parameters, allowing you to explore beyond the basic Mandelbrot and Julia sets. The combination of adjustable parameters makes the number of possible fractals effectively infinite."
    icon: ⚙️

---


<style>
.Layout.home {
    background-color: #1B1B1F;
    background-image: url("./assets/screenshot13.png");
    background-size: cover;
    background-position: center;
    background-blend-mode: overlay;
}

.VPFeature {
    background-color: #2021277a !important;
    backdrop-filter: blur(25px)
}
</style>
