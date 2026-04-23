window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: '.*|',
    processHtmlClass: 'arithmatex'
  },
  svg: {
    fontCache: 'global'
  },
  startup: {
    ready: () => {
      MathJax.startup.defaultReady();
      
      // Re-typeset math when navigation.instant loads new content
      // Wait for document$ to be available, then subscribe to navigation events
      const setupNavigationListener = () => {
        if (typeof document$ !== 'undefined') {
          document$.subscribe(() => {
            MathJax.typesetPromise();
          });
        } else {
          // Fallback: retry after a short delay
          setTimeout(setupNavigationListener, 100);
        }
      };
      
      setupNavigationListener();
    }
  }
};

