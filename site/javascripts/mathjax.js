window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: '.*|',
    processHtmlClass: 'arithmatex',
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  },
  svg: {
    fontCache: 'global'
  },
  startup: {
    typeset: false,
    ready: () => {
      MathJax.startup.defaultReady();
      console.log('MathJax ready, setting up navigation listener...');
      
      // Function to reinitialize MathJax for new content
      const reinitializeMathJax = () => {
        console.log('Reinitializing MathJax for new content...');
        
        // Clear all existing MathJax elements
        const existingMathElements = document.querySelectorAll('.MathJax, mjx-container');
        existingMathElements.forEach(el => {
          if (el.parentNode) {
            el.parentNode.replaceChild(document.createTextNode(el.textContent || ''), el);
          }
        });
        
        // Find and restore original math elements
        const arithmatexElements = document.querySelectorAll('.arithmatex');
        arithmatexElements.forEach(el => {
          if (el.classList.contains('MathJax')) {
            el.classList.remove('MathJax');
          }
        });
        
        // Wait a moment for DOM to settle, then re-typeset
        setTimeout(() => {
          MathJax.typesetPromise().then(() => {
            console.log('MathJax reinitialization completed');
          }).catch((error) => {
            console.error('MathJax reinitialization failed:', error);
          });
        }, 50);
      };
      
      // Re-typeset math when navigation.instant loads new content
      const setupNavigationListener = () => {
        if (typeof document$ !== 'undefined') {
          console.log('document$ found, subscribing to navigation events');
          document$.subscribe(() => {
            console.log('Navigation event detected, reinitializing MathJax...');
            setTimeout(reinitializeMathJax, 100);
          });
        } else {
          console.log('document$ not found, retrying in 100ms...');
          setTimeout(setupNavigationListener, 100);
        }
      };
      
      setupNavigationListener();
      
      // Initial typeset
      MathJax.typesetPromise().then(() => {
        console.log('Initial MathJax typeset completed');
      });
    }
  }
};

