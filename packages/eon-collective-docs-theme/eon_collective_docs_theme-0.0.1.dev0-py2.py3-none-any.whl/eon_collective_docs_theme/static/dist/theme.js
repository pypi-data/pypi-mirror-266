/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./js/theme.js":
/*!*********************!*\
  !*** ./js/theme.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _sass_theme_scss__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../sass/theme.scss */ "./sass/theme.scss");
/* harmony import */ var autocompleter__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! autocompleter */ "./node_modules/autocompleter/autocomplete.js");
/* harmony import */ var autocompleter__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(autocompleter__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var bootstrap__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! bootstrap */ "./node_modules/bootstrap/dist/js/bootstrap.js");
/* harmony import */ var bootstrap__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(bootstrap__WEBPACK_IMPORTED_MODULE_2__);
// T3Docs




// Ensure our own namespace
if (typeof window.T3Docs === 'undefined') {
  window.T3Docs = {};
}

/**
 * Inject collapsible menu
 */
function makeMenuExpandable() {
  function toggleCurrent(event) {
    const expandButton = event.currentTarget;
    const element = expandButton.parentElement;
    const siblings = element.parentElement.parentElement.querySelectorAll('li.current');
    siblings.forEach(sibling => {
      if (sibling !== element) {
        sibling.classList.remove('current');
      }
    });
    element.classList.toggle('current');
  }
  const toc = document.querySelector('.toc');
  const links = Array.from(toc.getElementsByTagName('a'));
  const template = document.querySelector('[data-toggle-item-template]');
  const templateChild = template.content.firstElementChild;
  links.forEach(link => {
    if (link.nextSibling) {
      const expandButton = templateChild.cloneNode(true);
      expandButton.addEventListener('click', toggleCurrent, true);
      link.before(expandButton);
    }
  });
}
makeMenuExpandable();

// Wrap tables to make them responsive
function makeTablesResponsive() {
  var tables = document.querySelectorAll('.rst-content table.docutils');
  for (var i = 0; i < tables.length; i++) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('table-responsive');
    tables[i].parentNode.insertBefore(wrapper, tables[i]);
    wrapper.appendChild(tables[i]);
  }
}
makeTablesResponsive();
document.addEventListener('DOMContentLoaded', () => {
  // Wire up light/dark mode button.
  document.getElementById('wagtail-theme').addEventListener('click', event => {
    document.dispatchEvent(new CustomEvent('theme:toggle-theme-mode', event));
  });

  // Search.
  var searchform = document.getElementById('search-form');
  var searchinput = document.getElementById('searchinput');
  if (searchform && searchinput) {
    autocompleter__WEBPACK_IMPORTED_MODULE_1___default()({
      input: searchinput,
      fetch: (text, update) => {
        // Populate autocomplete suggestions from the Sphinx `Search` object.
        if (typeof window.T3Docs.autocomplete === 'undefined') {
          window.T3Docs.autocomplete = [];
          // Add page titles first.
          Object.keys(Search._index.titles).forEach(item => {
            window.T3Docs.autocomplete.push({
              label: Search._index.titles[item],
              docname: Search._index.docnames[item],
              group: 'Pages'
            });
          });
          // Add autodoc/code terms second.
          Object.keys(Search._index.objects).forEach(item => {
            Object.keys(Search._index.objects[item]).forEach(subitem => {
              window.T3Docs.autocomplete.push({
                label: `${item}.${subitem}`,
                group: 'Code reference'
              });
            });
          });
        }
        var suggestions = window.T3Docs.autocomplete.filter(entry => entry.label.toLowerCase().includes(text.toLowerCase()));
        update(suggestions);
      },
      minLength: 3,
      render: item => {
        var div = document.createElement('div');
        div.textContent = item.label;
        return div;
      },
      customize: (input, inputRect, container) => {
        // Do not force same width as input box - allow it to go wider.
        // eslint-disable-next-line no-param-reassign
        container.style.minWidth = inputRect.width + 'px';
        // eslint-disable-next-line no-param-reassign
        container.style.width = 'auto';
      },
      onSelect: item => {
        // If they selected a page, disable search form and go straight to it.
        if (item.docname !== undefined) {
          searchform.onsubmit = function onsubmit() {
            return false;
          };
          // Figure out the URL from the docname.
          // Mostly taken from Sphinx's searchtools.js
          var linkUrl;
          if (DOCUMENTATION_OPTIONS.BUILDER === 'dirhtml') {
            var dirname = item.docname + '/';
            if (dirname.match(/\/index\/$/)) {
              dirname = dirname.substring(0, dirname.length - 6);
            } else if (dirname === 'index/') {
              dirname = '';
            }
            linkUrl = DOCUMENTATION_OPTIONS.URL_ROOT + dirname;
          } else {
            // normal html builders
            linkUrl = DOCUMENTATION_OPTIONS.URL_ROOT + item.docname + DOCUMENTATION_OPTIONS.FILE_SUFFIX;
          }
          // Go to the URL.
          window.location.href = linkUrl;
        }
        // Otherwise submit the query.
        else {
          searchinput.value = item.label;
          searchform.submit();
        }
      }
    });
  }
});

/***/ }),

/***/ "./sass/theme.scss":
/*!*************************!*\
  !*** ./sass/theme.scss ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/chunk loaded */
/******/ 	(() => {
/******/ 		var deferred = [];
/******/ 		__webpack_require__.O = (result, chunkIds, fn, priority) => {
/******/ 			if(chunkIds) {
/******/ 				priority = priority || 0;
/******/ 				for(var i = deferred.length; i > 0 && deferred[i - 1][2] > priority; i--) deferred[i] = deferred[i - 1];
/******/ 				deferred[i] = [chunkIds, fn, priority];
/******/ 				return;
/******/ 			}
/******/ 			var notFulfilled = Infinity;
/******/ 			for (var i = 0; i < deferred.length; i++) {
/******/ 				var [chunkIds, fn, priority] = deferred[i];
/******/ 				var fulfilled = true;
/******/ 				for (var j = 0; j < chunkIds.length; j++) {
/******/ 					if ((priority & 1 === 0 || notFulfilled >= priority) && Object.keys(__webpack_require__.O).every((key) => (__webpack_require__.O[key](chunkIds[j])))) {
/******/ 						chunkIds.splice(j--, 1);
/******/ 					} else {
/******/ 						fulfilled = false;
/******/ 						if(priority < notFulfilled) notFulfilled = priority;
/******/ 					}
/******/ 				}
/******/ 				if(fulfilled) {
/******/ 					deferred.splice(i--, 1)
/******/ 					var r = fn();
/******/ 					if (r !== undefined) result = r;
/******/ 				}
/******/ 			}
/******/ 			return result;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"theme": 0
/******/ 		};
/******/ 		
/******/ 		// no chunk on demand loading
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		__webpack_require__.O.j = (chunkId) => (installedChunks[chunkId] === 0);
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 			return __webpack_require__.O(result);
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkeon_collective_docs_theme"] = self["webpackChunkeon_collective_docs_theme"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module depends on other loaded chunks and execution need to be delayed
/******/ 	var __webpack_exports__ = __webpack_require__.O(undefined, ["vendor"], () => (__webpack_require__("./js/theme.js")))
/******/ 	__webpack_exports__ = __webpack_require__.O(__webpack_exports__);
/******/ 	
/******/ })()
;
//# sourceMappingURL=theme.js.map