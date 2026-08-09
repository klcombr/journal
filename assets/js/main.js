(function () {
  "use strict";

  /* ---------- Theme ---------- */
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("journal-theme"); } catch (e) {}

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem("journal-theme", theme); } catch (e) {}
  }

  if (!saved) {
    saved = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches
      ? "light"
      : "dark";
  }
  applyTheme(saved);

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  }

  /* ---------- Mobile menu ---------- */
  var menuBtn = document.getElementById("menu-toggle");
  var navLinks = document.querySelector(".nav-links");
  if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function () {
      navLinks.classList.toggle("open");
    });
    navLinks.addEventListener("click", function (e) {
      if (e.target.tagName === "A") navLinks.classList.remove("open");
    });
  }

  /* ---------- Stars ---------- */
  var canvas = document.getElementById("stars");
  if (canvas) {
    var ctx = canvas.getContext("2d");
    var stars = [];
    var count = 90;
    function resize() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
      stars = [];
      for (var i = 0; i < count; i++) {
        stars.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          r: Math.random() * 1.4 + 0.3,
          s: Math.random() * 0.6 + 0.2,
        });
      }
    }
    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      stars.forEach(function (st) {
        var twinkle = 0.4 + 0.6 * Math.abs(Math.sin(Date.now() * 0.002 * st.s));
        ctx.beginPath();
        ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(148, 163, 199, " + twinkle.toFixed(2) + ")";
        ctx.fill();
      });
      requestAnimationFrame(draw);
    }
    resize();
    window.addEventListener("resize", resize);
    draw();
  }

  /* ---------- Animated counters ---------- */
  var counters = document.querySelectorAll(".stat-num[data-count]");
  var counted = false;
  function animateCounters() {
    if (counted) return;
    counted = true;
    counters.forEach(function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10);
      var start = null;
      var dur = 1200;
      function step(ts) {
        if (!start) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        el.textContent = Math.floor(p * target);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target;
      }
      requestAnimationFrame(step);
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var cards = document.querySelectorAll(".card, .terminal, .code-block, details");
  cards.forEach(function (el) { el.classList.add("reveal"); });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        en.target.classList.add("visible");
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.12 });

  cards.forEach(function (el) { io.observe(el); });

  var statsEl = document.getElementById("stats");
  if (statsEl && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { animateCounters(); io.disconnect(); }
      });
    }, { threshold: 0.4 }).observe(statsEl);
  } else {
    animateCounters();
  }

  /* ---------- Footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
