/**
* Template Name: Company - v4.7.0
* Template URL: https://bootstrapmade.com/company-free-html-bootstrap-template/
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Mobile nav toggle (toggle is now outside #navbar)
   */
  const navbar = select('#navbar');
  const mobileNavToggle = select('.mobile-nav-toggle');
  
  if (mobileNavToggle && navbar) {
    mobileNavToggle.addEventListener('click', function(e) {
      navbar.classList.toggle('navbar-mobile');
      document.body.classList.toggle('mobile-nav-open');
      this.classList.toggle('bi-list');
      this.classList.toggle('bi-x');
    });

    // Close the mobile menu only when a non-dropdown link is clicked
    const allLinks = navbar.querySelectorAll('ul li a');
    allLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        const parentLi = this.parentElement;
        if (parentLi.classList.contains('dropdown') && this.nextElementSibling && this.nextElementSibling.tagName === 'UL') {
          return;
        }
        navbar.classList.remove('navbar-mobile');
        document.body.classList.remove('mobile-nav-open');
        mobileNavToggle.classList.add('bi-list');
        mobileNavToggle.classList.remove('bi-x');
      });
    });
  }

  /**
   * Mobile nav dropdowns activate (FIXED – removes clipping)
   */
  on('click', '.navbar .dropdown > a', function(e) {
    if (select('#navbar').classList.contains('navbar-mobile')) {
      e.preventDefault();
      
      const dropdownUl = this.nextElementSibling;
      dropdownUl.classList.toggle('dropdown-active');
      
      // Find the scrollable container (the main <ul> inside navbar-mobile)
      const scrollContainer = this.closest('ul');
      if (scrollContainer) {
        // If any dropdown is active, allow overflow to show it
        const anyActive = scrollContainer.querySelector('.dropdown-active');
        scrollContainer.style.overflow = anyActive ? 'visible' : '';
      }
    }
  }, true);

  /**
   * Hero carousel indicators
   */
  let heroCarouselIndicators = select("#hero-carousel-indicators")
  let heroCarouselItems = select('#heroCarousel .carousel-item', true)

  if (heroCarouselIndicators && heroCarouselItems) {
    heroCarouselItems.forEach((item, index) => {
      (index === 0) ?
      heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "' class='active'></li>":
        heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "'></li>"
    });
  }

  /**
   * Porfolio isotope and filter
   */
  window.addEventListener('load', () => {
    let portfolioContainer = select('.portfolio-container');
    if (portfolioContainer) {
      let portfolioIsotope = new Isotope(portfolioContainer, {
        itemSelector: '.portfolio-item'
      });

      let portfolioFilters = select('#portfolio-flters li', true);

      on('click', '#portfolio-flters li', function(e) {
        e.preventDefault();
        portfolioFilters.forEach(function(el) {
          el.classList.remove('filter-active');
        });
        this.classList.add('filter-active');

        portfolioIsotope.arrange({
          filter: this.getAttribute('data-filter')
        });
        portfolioIsotope.on('arrangeComplete', function() {
          AOS.refresh()
        });
      }, true);
    }

  });

  /**
   * Initiate portfolio lightbox 
   */
  if (typeof GLightbox !== 'undefined') {
    const portfolioLightbox = GLightbox({
      selector: '.portfolio-lightbox'
    });
  }

  /**
   * Portfolio details slider
   */
  if (typeof Swiper !== 'undefined') {
    new Swiper('.portfolio-details-slider', {
      speed: 400,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false
      },
      pagination: {
        el: '.swiper-pagination',
        type: 'bullets',
        clickable: true
      }
    });
  }

  /**
   * Skills animation
   */
  let skilsContent = select('.skills-content');
  if (skilsContent && typeof Waypoint !== 'undefined') {
    new Waypoint({
      element: skilsContent,
      offset: '80%',
      handler: function(direction) {
        let progress = select('.progress .progress-bar', true);
        progress.forEach((el) => {
          el.style.width = el.getAttribute('aria-valuenow') + '%'
        });
      }
    })
  }

  /**
   * Animation on scroll
   */
  window.addEventListener('load', () => {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 1000,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      })
    }
  });

})()