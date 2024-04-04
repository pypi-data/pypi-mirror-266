(window.webpackJsonpfeffery_utils_components=window.webpackJsonpfeffery_utils_components||[]).push([[27],{501:function(module,__webpack_exports__,__webpack_require__){"use strict";__webpack_require__.r(__webpack_exports__);var react__WEBPACK_IMPORTED_MODULE_0__=__webpack_require__(1),react__WEBPACK_IMPORTED_MODULE_0___default=__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__),_components_FefferyShortcutPanel_react__WEBPACK_IMPORTED_MODULE_1__=__webpack_require__(176),lodash__WEBPACK_IMPORTED_MODULE_2__=__webpack_require__(22),lodash__WEBPACK_IMPORTED_MODULE_2___default=__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_2__),ninja_keys__WEBPACK_IMPORTED_MODULE_3__=__webpack_require__(897),_components_FefferyStyle_react__WEBPACK_IMPORTED_MODULE_4__=__webpack_require__(90);function _typeof(e){return(_typeof="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function ownKeys(t,e){var n,r=Object.keys(t);return Object.getOwnPropertySymbols&&(n=Object.getOwnPropertySymbols(t),e&&(n=n.filter(function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable})),r.push.apply(r,n)),r}function _objectSpread(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?ownKeys(Object(n),!0).forEach(function(e){_defineProperty(t,e,n[e])}):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):ownKeys(Object(n)).forEach(function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))})}return t}function _defineProperty(e,t,n){(t=_toPropertyKey(t))in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n}function _toPropertyKey(e){e=_toPrimitive(e,"string");return"symbol"==_typeof(e)?e:String(e)}function _toPrimitive(e,t){if("object"!=_typeof(e)||!e)return e;var n=e[Symbol.toPrimitive];if(void 0===n)return("string"===t?String:Number)(e);n=n.call(e,t||"default");if("object"!=_typeof(n))return n;throw new TypeError("@@toPrimitive must return a primitive value.")}var footerHtmlEn=react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("div",{class:"modal-footer",slot:"footer"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{class:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"enter"),"to select"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",className:"ninja-examplekey",viewBox:"0 0 24 24"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M0 0h24v24H0V0z",fill:"none"}),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"})),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",className:"ninja-examplekey",viewBox:"0 0 24 24"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M0 0h24v24H0V0z",fill:"none"}),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"})),"to navigate"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"esc"),"to close"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"backspace"),"move to parent")),footerHtmlZh=react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("div",{className:"modal-footer",slot:"footer"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"enter"),"选择"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",className:"ninja-examplekey",viewBox:"0 0 24 24"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M0 0h24v24H0V0z",fill:"none"}),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"})),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("svg",{xmlns:"http://www.w3.org/2000/svg",className:"ninja-examplekey",viewBox:"0 0 24 24"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M0 0h24v24H0V0z",fill:"none"}),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("path",{d:"M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"})),"上下切换"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"esc"),"关闭面板"),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"help"},react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("span",{className:"ninja-examplekey esc"},"backspace"),"回到上一级")),locale2footer=new Map([["en",footerHtmlEn],["zh",footerHtmlZh]]),locale2placeholder=new Map([["en","Type a command or search..."],["zh","输入指令或进行搜索..."]]),FefferyShortcutPanel=function FefferyShortcutPanel(props){var id=props.id,data=props.data,placeholder=props.placeholder,openHotkey=props.openHotkey,theme=props.theme,locale=props.locale,open=props.open,close=props.close,panelStyles=props.panelStyles,setProps=props.setProps,loading_state=props.loading_state,data=data.map(function(e){return Object(lodash__WEBPACK_IMPORTED_MODULE_2__.isString)(e.handler)||e.hasOwnProperty("children")?e:_objectSpread(_objectSpread({},e),{handler:function(){setProps({triggeredHotkey:{id:e.id,timestamp:Date.parse(new Date)}})}})}),ninjaKeys=Object(react__WEBPACK_IMPORTED_MODULE_0__.useRef)(null);return Object(react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(function(){ninjaKeys.current&&ninjaKeys.current.addEventListener("change",function(e){setProps({searchValue:e.detail.search})})},[]),Object(react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(function(){ninjaKeys.current&&(ninjaKeys.current.data=data.map(function(item){return Object(lodash__WEBPACK_IMPORTED_MODULE_2__.isString)(item.handler)?_objectSpread(_objectSpread({},item),{handler:eval(item.handler)}):item}))},[data]),Object(react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(function(){ninjaKeys.current&&open&&(ninjaKeys.current.open(),setProps({open:!1}))},[open]),Object(react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(function(){ninjaKeys.current&&close&&(ninjaKeys.current.close(),setProps({close:!1}))},[close]),panelStyles=_objectSpread(_objectSpread({},{width:"640px",overflowBackground:"rgba(255, 255, 255, 0.5)",textColor:"rgb(60, 65, 73)",fontSize:"16px",top:"20%",accentColor:"rgb(110, 94, 210)",secondaryBackgroundColor:"rgb(239, 241, 244)",secondaryTextColor:"rgb(107, 111, 118)",selectedBackground:"rgb(248, 249, 251)",actionsHeight:"300px",groupTextColor:"rgb(144, 149, 157)",zIndex:1}),panelStyles),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement(react__WEBPACK_IMPORTED_MODULE_0___default.a.Fragment,null,react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement(_components_FefferyStyle_react__WEBPACK_IMPORTED_MODULE_4__.a,{rawStyle:"\nninja-keys {\n    --ninja-width: ".concat(panelStyles.width,";\n    --ninja-overflow-background: ").concat(panelStyles.overflowBackground,";\n    --ninja-text-color: ").concat(panelStyles.textColor,";\n    --ninja-font-size: ").concat(panelStyles.fontSize,";\n    --ninja-top: ").concat(panelStyles.top,";\n    --ninja-accent-color: ").concat(panelStyles.accentColor,";\n    --ninja-secondary-background-color: ").concat(panelStyles.secondaryBackgroundColor,";\n    --ninja-secondary-text-color: ").concat(panelStyles.secondaryTextColor,";\n    --ninja-selected-background: ").concat(panelStyles.selectedBackground,";\n    --ninja-actions-height: ").concat(panelStyles.actionsHeight,";\n    --ninja-group-text-color: ").concat(panelStyles.groupTextColor,";\n    --ninja-z-index: ").concat(panelStyles.zIndex,";\n}\n")}),react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("ninja-keys",{id:id,class:theme,ref:ninjaKeys,placeholder:placeholder||locale2placeholder.get(locale),openHotkey:openHotkey,hotKeysJoinedView:!0,hideBreadcrumbs:!0,"data-dash-is-loading":loading_state&&loading_state.is_loading||void 0},locale2footer.get(locale)))};__webpack_exports__.default=FefferyShortcutPanel,FefferyShortcutPanel.defaultProps=_components_FefferyShortcutPanel_react__WEBPACK_IMPORTED_MODULE_1__.b,FefferyShortcutPanel.propTypes=_components_FefferyShortcutPanel_react__WEBPACK_IMPORTED_MODULE_1__.c},897:function(R,B,e){"use strict";function H(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=new Array(t);n<t;n++)r[n]=e[n];return r}function I(e){return(I="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function U(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,function(e){e=function(e){if("object"!=I(e)||!e)return e;var t=e[Symbol.toPrimitive];if(void 0===t)return String(e);t=t.call(e,"string");if("object"!=I(t))return t;throw new TypeError("@@toPrimitive must return a primitive value.")}(e);return"symbol"==I(e)?e:String(e)}(r.key),r)}}function K(r){for(var e=arguments.length,t=new Array(1<e?e-1:0),n=1;n<e;n++)t[n-1]=arguments[n];var o=1===r.length?r[0]:t.reduce(function(e,t,n){return e+function(){if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")}()+r[n+1]},r[0]);return new F(o,r,W)}var N=window,z=N.ShadowRoot&&(void 0===N.ShadyCSS||N.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,W=Symbol(),V=new WeakMap,F=(U((t=q).prototype,[{key:"styleSheet",get:function(){var e,t=this.o,n=this.t;return z&&void 0===t&&void 0===(t=(e=void 0!==n&&1===n.length)?V.get(n):t)&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),e)&&V.set(n,t),t}},{key:"toString",value:function(){return this.cssText}}]),Object.defineProperty(t,"prototype",{writable:!1}),q),G=z?function(e){return e}:function(e){if(e instanceof CSSStyleSheet){var t,n="",r=function(e,t){var n,r,o,i,a="undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(a)return o=!(r=!0),{s:function(){a=a.call(e)},n:function(){var e=a.next();return r=e.done,e},e:function(e){o=!0,n=e},f:function(){try{r||null==a.return||a.return()}finally{if(o)throw n}}};if(Array.isArray(e)||(a=function(e){var t;if(e)return"string"==typeof e?H(e,void 0):"Map"===(t="Object"===(t=Object.prototype.toString.call(e).slice(8,-1))&&e.constructor?e.constructor.name:t)||"Set"===t?Array.from(e):"Arguments"===t||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t)?H(e,void 0):void 0}(e))||t&&e&&"number"==typeof e.length)return a&&(e=a),i=0,{s:t=function(){},n:function(){return i>=e.length?{done:!0}:{done:!1,value:e[i++]}},e:function(e){throw e},f:t};throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}(e.cssRules);try{for(r.s();!(t=r.n()).done;)n+=t.value.cssText}catch(e){r.e(e)}finally{r.f()}return new F("string"==typeof n?n:n+"",void 0,W)}return e};function q(e,t,n){if(!(this instanceof q))throw new TypeError("Cannot call a class as a function");if(this._$cssResult$=!0,n!==W)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}function J(e,t){var n,r,o,i,a="undefined"!=typeof Symbol&&e[Symbol.iterator]||e["@@iterator"];if(a)return o=!(r=!0),{s:function(){a=a.call(e)},n:function(){var e=a.next();return r=e.done,e},e:function(e){o=!0,n=e},f:function(){try{r||null==a.return||a.return()}finally{if(o)throw n}}};if(Array.isArray(e)||(a=Q(e))||t&&e&&"number"==typeof e.length)return a&&(e=a),i=0,{s:t=function(){},n:function(){return i>=e.length?{done:!0}:{done:!1,value:e[i++]}},e:function(e){throw e},f:t};throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}function Z(e){return function(e){if(Array.isArray(e))return Y(e)}(e)||function(){if("undefined"!=typeof Symbol&&null!=e[Symbol.iterator]||null!=e["@@iterator"])return Array.from(e)}()||Q(e)||function(){throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}()}function Q(e,t){var n;if(e)return"string"==typeof e?Y(e,t):"Map"===(n="Object"===(n=Object.prototype.toString.call(e).slice(8,-1))&&e.constructor?e.constructor.name:n)||"Set"===n?Array.from(e):"Arguments"===n||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)?Y(e,t):void 0}function Y(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=new Array(t);n<t;n++)r[n]=e[n];return r}function O(e){return(O="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function X(){X=function(){return a};var l,a={},e=Object.prototype,c=e.hasOwnProperty,u=Object.defineProperty||function(e,t,n){e[t]=n.value},t="function"==typeof Symbol?Symbol:{},r=t.iterator||"@@iterator",n=t.asyncIterator||"@@asyncIterator",o=t.toStringTag||"@@toStringTag";function i(e,t,n){return Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}),e[t]}try{i({},"")}catch(l){i=function(e,t,n){return e[t]=n}}function s(e,t,n,r){var o,i,a,s,t=t&&t.prototype instanceof y?t:y,t=Object.create(t.prototype),r=new j(r||[]);return u(t,"_invoke",{value:(o=e,i=n,a=r,s=d,function(e,t){if(s===p)throw new Error("Generator is already running");if(s===f){if("throw"===e)throw t;return{value:l,done:!0}}for(a.method=e,a.arg=t;;){var n=a.delegate;if(n){n=function e(t,n){var r=n.method,o=t.iterator[r];if(o===l)return n.delegate=null,"throw"===r&&t.iterator.return&&(n.method="return",n.arg=l,e(t,n),"throw"===n.method)||"return"!==r&&(n.method="throw",n.arg=new TypeError("The iterator does not provide a '"+r+"' method")),_;r=h(o,t.iterator,n.arg);if("throw"===r.type)return n.method="throw",n.arg=r.arg,n.delegate=null,_;o=r.arg;return o?o.done?(n[t.resultName]=o.value,n.next=t.nextLoc,"return"!==n.method&&(n.method="next",n.arg=l),n.delegate=null,_):o:(n.method="throw",n.arg=new TypeError("iterator result is not an object"),n.delegate=null,_)}(n,a);if(n){if(n===_)continue;return n}}if("next"===a.method)a.sent=a._sent=a.arg;else if("throw"===a.method){if(s===d)throw s=f,a.arg;a.dispatchException(a.arg)}else"return"===a.method&&a.abrupt("return",a.arg);s=p;n=h(o,i,a);if("normal"===n.type){if(s=a.done?f:"suspendedYield",n.arg===_)continue;return{value:n.arg,done:a.done}}"throw"===n.type&&(s=f,a.method="throw",a.arg=n.arg)}})}),t}function h(e,t,n){try{return{type:"normal",arg:e.call(t,n)}}catch(e){return{type:"throw",arg:e}}}a.wrap=s;var d="suspendedStart",p="executing",f="completed",_={};function y(){}function v(){}function m(){}var t={},b=(i(t,r,function(){return this}),Object.getPrototypeOf),b=b&&b(b(A([]))),g=(b&&b!==e&&c.call(b,r)&&(t=b),m.prototype=y.prototype=Object.create(t));function w(e){["next","throw","return"].forEach(function(t){i(e,t,function(e){return this._invoke(t,e)})})}function E(a,s){var t;u(this,"_invoke",{value:function(n,r){function e(){return new s(function(e,t){!function t(e,n,r,o){var i,e=h(a[e],a,n);if("throw"!==e.type)return(n=(i=e.arg).value)&&"object"==O(n)&&c.call(n,"__await")?s.resolve(n.__await).then(function(e){t("next",e,r,o)},function(e){t("throw",e,r,o)}):s.resolve(n).then(function(e){i.value=e,r(i)},function(e){return t("throw",e,r,o)});o(e.arg)}(n,r,e,t)})}return t=t?t.then(e,e):e()}})}function k(e){var t={tryLoc:e[0]};1 in e&&(t.catchLoc=e[1]),2 in e&&(t.finallyLoc=e[2],t.afterLoc=e[3]),this.tryEntries.push(t)}function $(e){var t=e.completion||{};t.type="normal",delete t.arg,e.completion=t}function j(e){this.tryEntries=[{tryLoc:"root"}],e.forEach(k,this),this.reset(!0)}function A(t){if(t||""===t){var n,e=t[r];if(e)return e.call(t);if("function"==typeof t.next)return t;if(!isNaN(t.length))return n=-1,(e=function e(){for(;++n<t.length;)if(c.call(t,n))return e.value=t[n],e.done=!1,e;return e.value=l,e.done=!0,e}).next=e}throw new TypeError(O(t)+" is not iterable")}return u(g,"constructor",{value:v.prototype=m,configurable:!0}),u(m,"constructor",{value:v,configurable:!0}),v.displayName=i(m,o,"GeneratorFunction"),a.isGeneratorFunction=function(e){e="function"==typeof e&&e.constructor;return!!e&&(e===v||"GeneratorFunction"===(e.displayName||e.name))},a.mark=function(e){return Object.setPrototypeOf?Object.setPrototypeOf(e,m):(e.__proto__=m,i(e,o,"GeneratorFunction")),e.prototype=Object.create(g),e},a.awrap=function(e){return{__await:e}},w(E.prototype),i(E.prototype,n,function(){return this}),a.AsyncIterator=E,a.async=function(e,t,n,r,o){void 0===o&&(o=Promise);var i=new E(s(e,t,n,r),o);return a.isGeneratorFunction(t)?i:i.next().then(function(e){return e.done?e.value:i.next()})},w(g),i(g,o,"Generator"),i(g,r,function(){return this}),i(g,"toString",function(){return"[object Generator]"}),a.keys=function(e){var t,n=Object(e),r=[];for(t in n)r.push(t);return r.reverse(),function e(){for(;r.length;){var t=r.pop();if(t in n)return e.value=t,e.done=!1,e}return e.done=!0,e}},a.values=A,j.prototype={constructor:j,reset:function(e){if(this.prev=0,this.next=0,this.sent=this._sent=l,this.done=!1,this.delegate=null,this.method="next",this.arg=l,this.tryEntries.forEach($),!e)for(var t in this)"t"===t.charAt(0)&&c.call(this,t)&&!isNaN(+t.slice(1))&&(this[t]=l)},stop:function(){this.done=!0;var e=this.tryEntries[0].completion;if("throw"===e.type)throw e.arg;return this.rval},dispatchException:function(n){if(this.done)throw n;var r=this;function e(e,t){return i.type="throw",i.arg=n,r.next=e,t&&(r.method="next",r.arg=l),!!t}for(var t=this.tryEntries.length-1;0<=t;--t){var o=this.tryEntries[t],i=o.completion;if("root"===o.tryLoc)return e("end");if(o.tryLoc<=this.prev){var a=c.call(o,"catchLoc"),s=c.call(o,"finallyLoc");if(a&&s){if(this.prev<o.catchLoc)return e(o.catchLoc,!0);if(this.prev<o.finallyLoc)return e(o.finallyLoc)}else if(a){if(this.prev<o.catchLoc)return e(o.catchLoc,!0)}else{if(!s)throw new Error("try statement without catch or finally");if(this.prev<o.finallyLoc)return e(o.finallyLoc)}}}},abrupt:function(e,t){for(var n=this.tryEntries.length-1;0<=n;--n){var r=this.tryEntries[n];if(r.tryLoc<=this.prev&&c.call(r,"finallyLoc")&&this.prev<r.finallyLoc){var o=r;break}}var i=(o=o&&("break"===e||"continue"===e)&&o.tryLoc<=t&&t<=o.finallyLoc?null:o)?o.completion:{};return i.type=e,i.arg=t,o?(this.method="next",this.next=o.finallyLoc,_):this.complete(i)},complete:function(e,t){if("throw"===e.type)throw e.arg;return"break"===e.type||"continue"===e.type?this.next=e.arg:"return"===e.type?(this.rval=this.arg=e.arg,this.method="return",this.next="end"):"normal"===e.type&&t&&(this.next=t),_},finish:function(e){for(var t=this.tryEntries.length-1;0<=t;--t){var n=this.tryEntries[t];if(n.finallyLoc===e)return this.complete(n.completion,n.afterLoc),$(n),_}},catch:function(e){for(var t=this.tryEntries.length-1;0<=t;--t){var n,r,o=this.tryEntries[t];if(o.tryLoc===e)return"throw"===(n=o.completion).type&&(r=n.arg,$(o)),r}throw new Error("illegal catch attempt")},delegateYield:function(e,t,n){return this.delegate={iterator:A(e),resultName:t,nextLoc:n},"next"===this.method&&(this.arg=l),_}},a}function ee(e,t,n,r,o,i,a){try{var s=e[i](a),l=s.value}catch(e){return n(e)}s.done?t(l):Promise.resolve(l).then(r,o)}function te(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,function(e){e=function(e){if("object"!=O(e)||!e)return e;var t=e[Symbol.toPrimitive];if(void 0===t)return String(e);t=t.call(e,"string");if("object"!=O(t))return t;throw new TypeError("@@toPrimitive must return a primitive value.")}(e);return"symbol"==O(e)?e:String(e)}(r.key),r)}}function ne(e){var n="function"==typeof Map?new Map:void 0;return function(e){if(null===e||!function(t){try{return-1!==Function.toString.call(t).indexOf("[native code]")}catch(e){return"function"==typeof t}}(e))return e;if("function"!=typeof e)throw new TypeError("Super expression must either be null or a function");if(void 0!==n){if(n.has(e))return n.get(e);n.set(e,t)}function t(){return function(e,t,n){var r;return re()?Reflect.construct.apply(null,arguments):((r=[null]).push.apply(r,t),t=new(e.bind.apply(e,r)),n&&oe(t,n.prototype),t)}(e,arguments,ie(this).constructor)}return t.prototype=Object.create(e.prototype,{constructor:{value:t,enumerable:!1,writable:!0,configurable:!0}}),oe(t,e)}(e)}function re(){try{var e=!Boolean.prototype.valueOf.call(Reflect.construct(Boolean,[],function(){}))}catch(e){}return(re=function(){return!!e})()}function oe(e,t){return(oe=Object.setPrototypeOf?Object.setPrototypeOf.bind():function(e,t){return e.__proto__=t,e})(e,t)}function ie(e){return(ie=Object.setPrototypeOf?Object.getPrototypeOf.bind():function(e){return e.__proto__||Object.getPrototypeOf(e)})(e)}var t=window,n=t.trustedTypes,ae=n?n.emptyScript:"",n=t.reactiveElementPolyfillSupport,se={toAttribute:function(e,t){switch(t){case Boolean:e=e?ae:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e)}return e},fromAttribute:function(e,t){var n=e;switch(t){case Boolean:n=null!==e;break;case Number:n=null===e?null:Number(e);break;case Object:case Array:try{n=JSON.parse(e)}catch(e){n=null}}return n}},le=function(e,t){return t!==e&&(t==t||e==e)},ce={attribute:!0,type:String,converter:se,reflect:!1,hasChanged:le},r=function(e){function t(){var e;if(this instanceof t)return(e=function(e,t,n){t=ie(t);var r=e;if(!(t=re()?Reflect.construct(t,n||[],ie(e).constructor):t.apply(e,n))||"object"!==O(t)&&"function"!=typeof t){if(void 0!==t)throw new TypeError("Derived constructors may only return object or undefined");if(void 0===(t=r))throw new ReferenceError("this hasn't been initialised - super() hasn't been called")}return t}(this,t))._$Ei=new Map,e.isUpdatePending=!1,e.hasUpdated=!1,e._$El=null,e._$Eu(),e;throw new TypeError("Cannot call a class as a function")}var n,s,r,o=t;if("function"!=typeof e&&null!==e)throw new TypeError("Super expression must either be null or a function");return o.prototype=Object.create(e&&e.prototype,{constructor:{value:o,writable:!0,configurable:!0}}),Object.defineProperty(o,"prototype",{writable:!1}),e&&oe(o,e),o=t,e=[{key:"_$Eu",value:function(){var e,t=this;this._$E_=new Promise(function(e){return t.enableUpdating=e}),this._$AL=new Map,this._$Eg(),this.requestUpdate(),null!=(e=this.constructor.h)&&e.forEach(function(e){return e(t)})}},{key:"addController",value:function(e){var t;(null!=(t=this._$ES)?t:this._$ES=[]).push(e),void 0!==this.renderRoot&&this.isConnected&&null!=(t=e.hostConnected)&&t.call(e)}},{key:"removeController",value:function(e){var t;null!=(t=this._$ES)&&t.splice(this._$ES.indexOf(e)>>>0,1)}},{key:"_$Eg",value:function(){var n=this;this.constructor.elementProperties.forEach(function(e,t){n.hasOwnProperty(t)&&(n._$Ei.set(t,n[t]),delete n[t])})}},{key:"createRenderRoot",value:function(){var r,e,t=null!=(t=this.shadowRoot)?t:this.attachShadow(this.constructor.shadowRootOptions);return r=t,e=this.constructor.elementStyles,z?r.adoptedStyleSheets=e.map(function(e){return e instanceof CSSStyleSheet?e:e.styleSheet}):e.forEach(function(e){var t=document.createElement("style"),n=N.litNonce;void 0!==n&&t.setAttribute("nonce",n),t.textContent=e.cssText,r.appendChild(t)}),t}},{key:"connectedCallback",value:function(){var e;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null!=(e=this._$ES)&&e.forEach(function(e){var t;return null==(t=e.hostConnected)?void 0:t.call(e)})}},{key:"enableUpdating",value:function(e){}},{key:"disconnectedCallback",value:function(){var e;null!=(e=this._$ES)&&e.forEach(function(e){var t;return null==(t=e.hostDisconnected)?void 0:t.call(e)})}},{key:"attributeChangedCallback",value:function(e,t,n){this._$AK(e,n)}},{key:"_$EO",value:function(e,t){var n,r=2<arguments.length&&void 0!==arguments[2]?arguments[2]:ce,o=this.constructor._$Ep(e,r);void 0!==o&&!0===r.reflect&&(n=(void 0!==(null==(n=r.converter)?void 0:n.toAttribute)?r.converter:se).toAttribute(t,r.type),this._$El=e,null==n?this.removeAttribute(o):this.setAttribute(o,n),this._$El=null)}},{key:"_$AK",value:function(e,t){var n,r=this.constructor,e=r._$Ev.get(e);void 0!==e&&this._$El!==e&&(n="function"==typeof(r=r.getPropertyOptions(e)).converter?{fromAttribute:r.converter}:void 0!==(null==(n=r.converter)?void 0:n.fromAttribute)?r.converter:se,this._$El=e,this[e]=n.fromAttribute(t,r.type),this._$El=null)}},{key:"requestUpdate",value:function(e,t,n){var r=!0;void 0!==e&&(((n=n||this.constructor.getPropertyOptions(e)).hasChanged||le)(this[e],t)?(this._$AL.has(e)||this._$AL.set(e,t),!0===n.reflect&&this._$El!==e&&(void 0===this._$EC&&(this._$EC=new Map),this._$EC.set(e,n))):r=!1),!this.isUpdatePending&&r&&(this._$E_=this._$Ej())}},{key:"_$Ej",value:(s=X().mark(function e(){var t;return X().wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return this.isUpdatePending=!0,e.prev=1,e.next=4,this._$E_;case 4:e.next=9;break;case 6:e.prev=6,e.t0=e.catch(1),Promise.reject(e.t0);case 9:if(t=this.scheduleUpdate(),e.t1=null!=t,e.t1)return e.next=14,t;e.next=14;break;case 14:return e.abrupt("return",!this.isUpdatePending);case 15:case"end":return e.stop()}},e,this,[[1,6]])}),r=function(){var e=this,a=arguments;return new Promise(function(t,n){var r=s.apply(e,a);function o(e){ee(r,t,n,o,i,"next",e)}function i(e){ee(r,t,n,o,i,"throw",e)}o(void 0)})},function(){return r.apply(this,arguments)})},{key:"scheduleUpdate",value:function(){return this.performUpdate()}},{key:"performUpdate",value:function(){var e,n=this;if(this.isUpdatePending){this.hasUpdated,this._$Ei&&(this._$Ei.forEach(function(e,t){return n[t]=e}),this._$Ei=void 0);var t=!1,r=this._$AL;try{(t=this.shouldUpdate(r))?(this.willUpdate(r),null!=(e=this._$ES)&&e.forEach(function(e){var t;return null==(t=e.hostUpdate)?void 0:t.call(e)}),this.update(r)):this._$Ek()}catch(e){throw t=!1,this._$Ek(),e}t&&this._$AE(r)}}},{key:"willUpdate",value:function(e){}},{key:"_$AE",value:function(e){var t;null!=(t=this._$ES)&&t.forEach(function(e){var t;return null==(t=e.hostUpdated)?void 0:t.call(e)}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}},{key:"_$Ek",value:function(){this._$AL=new Map,this.isUpdatePending=!1}},{key:"updateComplete",get:function(){return this.getUpdateComplete()}},{key:"getUpdateComplete",value:function(){return this._$E_}},{key:"shouldUpdate",value:function(e){return!0}},{key:"update",value:function(e){var n=this;void 0!==this._$EC&&(this._$EC.forEach(function(e,t){return n._$EO(t,n[t],e)}),this._$EC=void 0),this._$Ek()}},{key:"updated",value:function(e){}},{key:"firstUpdated",value:function(e){}}],n=[{key:"addInitializer",value:function(e){var t;this.finalize(),(null!=(t=this.h)?t:this.h=[]).push(e)}},{key:"observedAttributes",get:function(){var n=this,r=(this.finalize(),[]);return this.elementProperties.forEach(function(e,t){e=n._$Ep(t,e);void 0!==e&&(n._$Ev.set(e,t),r.push(e))}),r}},{key:"createProperty",value:function(e){var t,n=1<arguments.length&&void 0!==arguments[1]?arguments[1]:ce;n.state&&(n.attribute=!1),this.finalize(),this.elementProperties.set(e,n),n.noAccessor||this.prototype.hasOwnProperty(e)||(t="symbol"==O(e)?Symbol():"__"+e,void 0!==(t=this.getPropertyDescriptor(e,t,n))&&Object.defineProperty(this.prototype,e,t))}},{key:"getPropertyDescriptor",value:function(n,r,o){return{get:function(){return this[r]},set:function(e){var t=this[n];this[r]=e,this.requestUpdate(n,t,o)},configurable:!0,enumerable:!0}}},{key:"getPropertyOptions",value:function(e){return this.elementProperties.get(e)||ce}},{key:"finalize",value:function(){if(this.hasOwnProperty("finalized"))return!1;this.finalized=!0;var e=Object.getPrototypeOf(this);if(e.finalize(),void 0!==e.h&&(this.h=Z(e.h)),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map,this.hasOwnProperty("properties")){var t,n=this.properties,r=J([].concat(Z(Object.getOwnPropertyNames(n)),Z(Object.getOwnPropertySymbols(n))));try{for(r.s();!(t=r.n()).done;){var o=t.value;this.createProperty(o,n[o])}}catch(e){r.e(e)}finally{r.f()}}return this.elementStyles=this.finalizeStyles(this.styles),!0}},{key:"finalizeStyles",value:function(e){var t=[];if(Array.isArray(e)){var n,r=J(new Set(e.flat(1/0).reverse()));try{for(r.s();!(n=r.n()).done;){var o=n.value;t.unshift(G(o))}}catch(e){r.e(e)}finally{r.f()}}else void 0!==e&&t.push(G(e));return t}},{key:"_$Ep",value:function(e,t){t=t.attribute;return!1===t?void 0:"string"==typeof t?t:"string"==typeof e?e.toLowerCase():void 0}}],te(o.prototype,e),te(o,n),Object.defineProperty(o,"prototype",{writable:!1}),t}(ne(HTMLElement));r.finalized=!0,r.elementProperties=new Map,r.elementStyles=[],r.shadowRootOptions={mode:"open"},null!=n&&n({ReactiveElement:r}),(null!=(n=t.reactiveElementVersions)?n:t.reactiveElementVersions=[]).push("1.6.3");const ue=window,c=ue.trustedTypes,he=c?c.createPolicy("lit-html",{createHTML:e=>e}):void 0,d=`lit$${(Math.random()+"").slice(9)}$`,de="?"+d,pe=`<${de}>`,l=document,u=()=>l.createComment(""),h=e=>null===e||"object"!=typeof e&&"function"!=typeof e,fe=Array.isArray,_e=e=>fe(e)||"function"==typeof(null==e?void 0:e[Symbol.iterator]),p=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ye=/-->/g,ve=/>/g,f=RegExp(">|[ \t\n\f\r](?:([^\\s\"'>=/]+)([ \t\n\f\r]*=[ \t\n\f\r]*(?:[^ \t\n\f\r\"'`<>=]|(\"|')|))|$)","g"),me=/'/g,be=/"/g,ge=/^(?:script|style|textarea|title)$/i,we=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),i=we(1),_=(we(2),Symbol.for("lit-noChange")),y=Symbol.for("lit-nothing"),Ee=new WeakMap,v=l.createTreeWalker(l,129,null,!1);function ke(e,t){if(Array.isArray(e)&&e.hasOwnProperty("raw"))return void 0!==he?he.createHTML(t):t;throw Error("invalid template strings array")}const $e=(i,e)=>{const a=i.length-1,s=[];let l,c=2===e?"<svg>":"",u=p;for(let o=0;o<a;o++){const a=i[o];let e,t,n=-1,r=0;for(;r<a.length&&(u.lastIndex=r,null!==(t=u.exec(a)));)r=u.lastIndex,u===p?"!--"===t[1]?u=ye:void 0!==t[1]?u=ve:void 0!==t[2]?(ge.test(t[2])&&(l=RegExp("</"+t[2],"g")),u=f):void 0!==t[3]&&(u=f):u===f?">"===t[0]?(u=null!=l?l:p,n=-1):void 0===t[1]?n=-2:(n=u.lastIndex-t[2].length,e=t[1],u=void 0===t[3]?f:'"'===t[3]?be:me):u===be||u===me?u=f:u===ye||u===ve?u=p:(u=f,l=void 0);var h=u===f&&i[o+1].startsWith("/>")?" ":"";c+=u===p?a+pe:0<=n?(s.push(e),a.slice(0,n)+"$lit$"+a.slice(n)+d+h):a+d+(-2===n?(s.push(void 0),o):h)}return[ke(i,c+(i[a]||"<?>")+(2===e?"</svg>":"")),s]};class je{constructor({strings:t,_$litType$:n},e){var r;this.parts=[];let o=0,i=0;var a=t.length-1,s=this.parts,[t,l]=$e(t,n);if(this.el=je.createElement(t,e),v.currentNode=this.el.content,2===n){const t=this.el.content,n=t.firstChild;n.remove(),t.append(...n.childNodes)}for(;null!==(r=v.nextNode())&&s.length<a;){if(1===r.nodeType){if(r.hasAttributes()){const t=[];for(const n of r.getAttributeNames())if(n.endsWith("$lit$")||n.startsWith(d)){const e=l[i++];if(t.push(n),void 0!==e){const t=r.getAttribute(e.toLowerCase()+"$lit$").split(d),n=/([.?@])?(.*)/.exec(e);s.push({type:1,index:o,name:n[2],strings:t,ctor:"."===n[1]?Oe:"?"===n[1]?Pe:"@"===n[1]?Se:g})}else s.push({type:6,index:o})}for(const n of t)r.removeAttribute(n)}if(ge.test(r.tagName)){const t=r.textContent.split(d),n=t.length-1;if(0<n){r.textContent=c?c.emptyScript:"";for(let e=0;e<n;e++)r.append(t[e],u()),v.nextNode(),s.push({type:2,index:++o});r.append(t[n],u())}}}else if(8===r.nodeType)if(r.data===de)s.push({type:2,index:o});else{let e=-1;for(;-1!==(e=r.data.indexOf(d,e+1));)s.push({type:7,index:o}),e+=d.length-1}o++}}static createElement(e,t){var n=l.createElement("template");return n.innerHTML=e,n}}function m(t,n,r=t,o){var i;if(n!==_){let e=void 0!==o?null==(a=r._$Co)?void 0:a[o]:r._$Cl;var a=h(n)?void 0:n._$litDirective$;(null==e?void 0:e.constructor)!==a&&(null!=(i=null==e?void 0:e._$AO)&&i.call(e,!1),void 0===a?e=void 0:(e=new a(t))._$AT(t,r,o),void 0!==o?(null!=(i=r._$Co)?i:r._$Co=[])[o]=e:r._$Cl=e),void 0!==e&&(n=m(t,e._$AS(t,n.values),e,o))}return n}class Ae{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){var{el:{content:e},parts:n}=this._$AD,r=(null!=(r=null==t?void 0:t.creationScope)?r:l).importNode(e,!0);v.currentNode=r;let o=v.nextNode(),i=0,a=0,s=n[0];for(;void 0!==s;){if(i===s.index){let e;2===s.type?e=new b(o,o.nextSibling,this,t):1===s.type?e=new s.ctor(o,s.name,s.strings,this,t):6===s.type&&(e=new Me(o,this,t)),this._$AV.push(e),s=n[++a]}i!==(null==s?void 0:s.index)&&(o=v.nextNode(),i++)}return v.currentNode=l,r}v(e){let t=0;for(const n of this._$AV)void 0!==n&&(void 0!==n.strings?(n._$AI(e,n,t),t+=n.strings.length-2):n._$AI(e[t])),t++}}class b{constructor(e,t,n,r){this.type=2,this._$AH=y,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=n,this.options=r,this._$Cp=null==(e=null==r?void 0:r.isConnected)||e}get _$AU(){var e;return null!=(e=null==(e=this._$AM)?void 0:e._$AU)?e:this._$Cp}get parentNode(){let e=this._$AA.parentNode;var t=this._$AM;return e=void 0!==t&&11===(null==e?void 0:e.nodeType)?t.parentNode:e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=m(this,e,t),h(e)?e===y||null==e||""===e?(this._$AH!==y&&this._$AR(),this._$AH=y):e!==this._$AH&&e!==_&&this._(e):void 0!==e._$litType$?this.g(e):void 0!==e.nodeType?this.$(e):_e(e)?this.T(e):this._(e)}k(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}$(e){this._$AH!==e&&(this._$AR(),this._$AH=this.k(e))}_(e){this._$AH!==y&&h(this._$AH)?this._$AA.nextSibling.data=e:this.$(l.createTextNode(e)),this._$AH=e}g(e){var t,{values:n,_$litType$:r}=e,r="number"==typeof r?this._$AC(e):(void 0===r.el&&(r.el=je.createElement(ke(r.h,r.h[0]),this.options)),r);if((null==(t=this._$AH)?void 0:t._$AD)===r)this._$AH.v(n);else{const e=new Ae(r,this),t=e.u(this.options);e.v(n),this.$(t),this._$AH=e}}_$AC(e){let t=Ee.get(e.strings);return void 0===t&&Ee.set(e.strings,t=new je(e)),t}T(e){fe(this._$AH)||(this._$AH=[],this._$AR());var t=this._$AH;let n,r=0;for(const o of e)r===t.length?t.push(n=new b(this.k(u()),this.k(u()),this,this.options)):n=t[r],n._$AI(o),r++;r<t.length&&(this._$AR(n&&n._$AB.nextSibling,r),t.length=r)}_$AR(e=this._$AA.nextSibling,t){var n;for(null!=(n=this._$AP)&&n.call(this,!1,!0,t);e&&e!==this._$AB;){const t=e.nextSibling;e.remove(),e=t}}setConnected(e){var t;void 0===this._$AM&&(this._$Cp=e,null!=(t=this._$AP))&&t.call(this,e)}}class g{constructor(e,t,n,r,o){this.type=1,this._$AH=y,this._$AN=void 0,this.element=e,this.name=t,this._$AM=r,this.options=o,2<n.length||""!==n[0]||""!==n[1]?(this._$AH=Array(n.length-1).fill(new String),this.strings=n):this._$AH=y}get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}_$AI(n,r=this,o,i){var a=this.strings;let s=!1;if(void 0===a)n=m(this,n,r,0),(s=!h(n)||n!==this._$AH&&n!==_)&&(this._$AH=n);else{const i=n;let e,t;for(n=a[0],e=0;e<a.length-1;e++)(t=m(this,i[o+e],r,e))===_&&(t=this._$AH[e]),s=s||!h(t)||t!==this._$AH[e],t===y?n=y:n!==y&&(n+=(null!=t?t:"")+a[e+1]),this._$AH[e]=t}s&&!i&&this.j(n)}j(e){e===y?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=e?e:"")}}class Oe extends g{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===y?void 0:e}}const xe=c?c.emptyScript:"";class Pe extends g{constructor(){super(...arguments),this.type=4}j(e){e&&e!==y?this.element.setAttribute(this.name,xe):this.element.removeAttribute(this.name)}}class Se extends g{constructor(e,t,n,r,o){super(e,t,n,r,o),this.type=5}_$AI(e,t=this){var n,r;(e=null!=(t=m(this,e,t,0))?t:y)!==_&&(t=this._$AH,n=e===y&&t!==y||e.capture!==t.capture||e.once!==t.once||e.passive!==t.passive,r=e!==y&&(t===y||n),n&&this.element.removeEventListener(this.name,this,t),r&&this.element.addEventListener(this.name,this,e),this._$AH=e)}handleEvent(e){var t;"function"==typeof this._$AH?this._$AH.call(null!=(t=null==(t=this.options)?void 0:t.host)?t:this.element,e):this._$AH.handleEvent(e)}}class Me{constructor(e,t,n){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=n}get _$AU(){return this._$AM._$AU}_$AI(e){m(this,e)}}var n={O:"$lit$",P:d,A:de,C:1,M:$e,L:Ae,R:_e,D:m,I:b,V:g,H:Pe,N:Se,U:Oe,F:Me},t=ue.litHtmlPolyfillSupport;null!=t&&t(je,b),(null!=(t=ue.litHtmlVersions)?t:ue.litHtmlVersions=[]).push("2.8.0");class o extends r{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){var e,t=super.createRenderRoot();return null==(e=this.renderOptions).renderBefore&&(e.renderBefore=t.firstChild),t}update(e){var t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,n)=>{var r,o=null!=(o=null==n?void 0:n.renderBefore)?o:t;let i=o._$litPart$;if(void 0===i){const e=null!=(r=null==n?void 0:n.renderBefore)?r:null;o._$litPart$=i=new b(t.insertBefore(u(),e),e,void 0,null!=n?n:{})}return i._$AI(e),i})(t,this.renderRoot,this.renderOptions)}connectedCallback(){var e;super.connectedCallback(),null!=(e=this._$Do)&&e.setConnected(!0)}disconnectedCallback(){var e;super.disconnectedCallback(),null!=(e=this._$Do)&&e.setConnected(!1)}render(){return _}}o.finalized=!0,o._$litElement$=!0,null!=(t=globalThis.litElementHydrateSupport)&&t.call(globalThis,{LitElement:o});function Ce(r){return function(e){return"function"==typeof e?(n=e,customElements.define(r,n),n):(t=r,{kind:e.kind,elements:e.elements,finisher:function(e){customElements.define(t,e)}});var t,n}}var r=globalThis.litElementPolyfillSupport;null!=r&&r({LitElement:o}),(null!=(t=globalThis.litElementVersions)?t:globalThis.litElementVersions=[]).push("3.3.3");function De(e){return(De="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function Le(t,e){var n,r=Object.keys(t);return Object.getOwnPropertySymbols&&(n=Object.getOwnPropertySymbols(t),e&&(n=n.filter(function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable})),r.push.apply(r,n)),r}function Te(o){for(var e=1;e<arguments.length;e++){var i=null!=arguments[e]?arguments[e]:{};e%2?Le(Object(i),!0).forEach(function(e){var t,n,r;t=o,n=i[e=e],r=function(e){if("object"!=De(e)||!e)return e;var t=e[Symbol.toPrimitive];if(void 0===t)return String(e);t=t.call(e,"string");if("object"!=De(t))return t;throw new TypeError("@@toPrimitive must return a primitive value.")}(e),(e="symbol"==De(r)?r:String(r))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n}):Object.getOwnPropertyDescriptors?Object.defineProperties(o,Object.getOwnPropertyDescriptors(i)):Le(Object(i)).forEach(function(e){Object.defineProperty(o,e,Object.getOwnPropertyDescriptor(i,e))})}return o}function a(o){return function(e,t){return void 0!==t?void e.constructor.createProperty(t,o):(n=o,"method"!==(r=e).kind||!r.descriptor||"value"in r.descriptor?{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:r.key,initializer:function(){"function"==typeof r.initializer&&(this[r.key]=r.initializer.call(this))},finisher:function(e){e.createProperty(r.key,n)}}:Te(Te({},r),{},{finisher:function(e){e.createProperty(r.key,n)}}));var n,r}}function Re(e){return(Re="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e})(e)}function Be(t,e){var n,r=Object.keys(t);return Object.getOwnPropertySymbols&&(n=Object.getOwnPropertySymbols(t),e&&(n=n.filter(function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable})),r.push.apply(r,n)),r}function He(o){for(var e=1;e<arguments.length;e++){var i=null!=arguments[e]?arguments[e]:{};e%2?Be(Object(i),!0).forEach(function(e){var t,n,r;t=o,n=i[e=e],r=function(e){if("object"!=Re(e)||!e)return e;var t=e[Symbol.toPrimitive];if(void 0===t)return String(e);t=t.call(e,"string");if("object"!=Re(t))return t;throw new TypeError("@@toPrimitive must return a primitive value.")}(e),(e="symbol"==Re(r)?r:String(r))in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n}):Object.getOwnPropertyDescriptors?Object.defineProperties(o,Object.getOwnPropertyDescriptors(i)):Be(Object(i)).forEach(function(e){Object.defineProperty(o,e,Object.getOwnPropertyDescriptor(i,e))})}return o}function s(e){return a(He(He({},e),{},{state:!0}))}null!=(r=window.HTMLSlotElement)&&r.prototype.assignedElements;const Ie=2,w=t=>(...e)=>({_$litDirective$:t,values:e});class E{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,n){this._$Ct=e,this._$AM=t,this._$Ci=n}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}}const Ue=n["I"],Ke=e=>void 0===e.strings,Ne=()=>document.createComment(""),k=(t,n,r)=>{var o,i=t._$AA.parentNode,a=void 0===n?t._$AB:n._$AA;if(void 0===r){const n=i.insertBefore(Ne(),a),o=i.insertBefore(Ne(),a);r=new Ue(n,o,t,t.options)}else{const n=r._$AB.nextSibling,s=r._$AM,e=s!==t;if(e){let e;null!=(o=r._$AQ)&&o.call(r,t),r._$AM=t,void 0!==r._$AP&&(e=t._$AU)!==s._$AU&&r._$AP(e)}if(n!==a||e){let e=r._$AA;for(;e!==n;){const n=e.nextSibling;i.insertBefore(e,a),e=n}}}return r},$=(e,t,n=e)=>(e._$AI(t,n),e),ze={},We=(e,t=ze)=>e._$AH=t,Ve=e=>{var t;null!=(t=e._$AP)&&t.call(e,!1,!0);let n=e._$AA;for(var r=e._$AB.nextSibling;n!==r;){const e=n.nextSibling;n.remove(),n=e}},Fe=(t,n,r)=>{var o=new Map;for(let e=n;e<=r;e++)o.set(t[e],e);return o},Ge=w(class extends E{constructor(e){if(super(e),e.type!==Ie)throw Error("repeat() can only be used in text expressions")}ct(e,t,n){let r;void 0===n?n=t:void 0!==t&&(r=t);var o=[],i=[];let a=0;for(const t of e)o[a]=r?r(t,a):a,i[a]=n(t,a),a++;return{values:i,keys:o}}render(e,t,n){return this.ct(e,t,n).values}update(e,[t,n,r]){var o=e._$AH,{values:i,keys:a}=this.ct(t,n,r);if(!Array.isArray(o))return this.ut=a,i;var s=null!=(t=this.ut)?t:this.ut=[],l=[];let c,u,h=0,d=o.length-1,p=0,f=i.length-1;for(;h<=d&&p<=f;)if(null===o[h])h++;else if(null===o[d])d--;else if(s[h]===a[p])l[p]=$(o[h],i[p]),h++,p++;else if(s[d]===a[f])l[f]=$(o[d],i[f]),d--,f--;else if(s[h]===a[f])l[f]=$(o[h],i[f]),k(e,l[f+1],o[h]),h++,f--;else if(s[d]===a[p])l[p]=$(o[d],i[p]),k(e,o[h],o[d]),d--,p++;else if(void 0===c&&(c=Fe(a,p,f),u=Fe(s,h,d)),c.has(s[h]))if(c.has(s[d])){const t=u.get(a[p]),n=void 0!==t?o[t]:null;if(null===n){const t=k(e,o[h]);$(t,i[p]),l[p]=t}else l[p]=$(n,i[p]),k(e,o[h],n),o[t]=null;p++}else Ve(o[d]),d--;else Ve(o[h]),h++;for(;p<=f;){const t=k(e,l[f+1]);$(t,i[p]),l[p++]=t}for(;h<=d;){const e=o[h++];null!==e&&Ve(e)}return this.ut=a,We(e,l),_}}),qe=w(class extends E{constructor(e){if(super(e),3!==e.type&&1!==e.type&&4!==e.type)throw Error("The `live` directive is not allowed on child or event bindings");if(!Ke(e))throw Error("`live` bindings can only contain a single expression")}render(e){return e}update(e,[t]){if(t!==_&&t!==y){var n=e.element,r=e.name;if(3===e.type){if(t===n[r])return _}else if(4===e.type){if(!!t===n.hasAttribute(r))return _}else if(1===e.type&&n.getAttribute(r)===t+"")return _;We(e)}return t}}),j=(e,t)=>{var n,r,o=e._$AN;if(void 0===o)return!1;for(const e of o)null!=(r=(n=e)._$AO)&&r.call(n,t,!1),j(e,t);return!0},Je=e=>{let t,n;for(;void 0!==(t=e._$AM)&&((n=t._$AN).delete(e),e=t,0===(null==n?void 0:n.size)););},Ze=n=>{for(let t;t=n._$AM;n=t){let e=t._$AN;if(void 0===e)t._$AN=e=new Set;else if(e.has(n))break;e.add(n),r=t,0,r.type==Ie&&(null==r._$AP&&(r._$AP=Ye),null==r._$AQ)&&(r._$AQ=Qe)}var r};function Qe(e){void 0!==this._$AN?(Je(this),this._$AM=e,Ze(this)):this._$AM=e}function Ye(e,t=!1,n=0){var r=this._$AH,o=this._$AN;if(void 0!==o&&0!==o.size)if(t)if(Array.isArray(r))for(let e=n;e<r.length;e++)j(r[e],!1),Je(r[e]);else null!=r&&(j(r,!1),Je(r));else j(this,e)}class Xe extends E{constructor(){super(...arguments),this._$AN=void 0}_$AT(e,t,n){super._$AT(e,t,n),Ze(this),this.isConnected=e._$AU}_$AO(e,t=!0){var n;e!==this.isConnected&&((this.isConnected=e)?null!=(n=this.reconnected)&&n.call(this):null!=(n=this.disconnected)&&n.call(this)),t&&(j(this,e),Je(this))}setValue(e){var t;Ke(this._$Ct)?this._$Ct._$AI(e,this):((t=[...this._$Ct._$AH])[this._$Ci]=e,this._$Ct._$AI(t,this,0))}disconnected(){}reconnected(){}}const et=()=>new tt;class tt{}const nt=new WeakMap,rt=w(class extends Xe{render(e){return y}update(e,[t]){var n=t!==this.G;return n&&void 0!==this.G&&this.ot(void 0),!n&&this.rt===this.lt||(this.G=t,this.dt=null==(n=e.options)?void 0:n.host,this.ot(this.lt=e.element)),y}ot(t){if("function"==typeof this.G){var n=null!=(n=this.dt)?n:globalThis;let e=nt.get(n);void 0===e&&(e=new WeakMap,nt.set(n,e)),void 0!==e.get(this.G)&&this.G.call(this.dt,void 0),e.set(this.G,t),void 0!==t&&this.G.call(this.dt,t)}else this.G.value=t}get rt(){var e;return"function"==typeof this.G?null==(e=nt.get(null!=(e=this.dt)?e:globalThis))?void 0:e.get(this.G):null==(e=this.G)?void 0:e.value}disconnected(){this.rt===this.lt&&this.ot(void 0)}reconnected(){this.ot(this.lt)}}),ot=w(class extends E{constructor(e){if(super(e),1!==e.type||"class"!==e.name||2<(null==(e=e.strings)?void 0:e.length))throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter(e=>t[e]).join(" ")+" "}update(e,[t]){var n,r;if(void 0===this.it){this.it=new Set,void 0!==e.strings&&(this.nt=new Set(e.strings.join(" ").split(/\s/).filter(e=>""!==e)));for(const e in t)!t[e]||null!=(n=this.nt)&&n.has(e)||this.it.add(e);return this.render(t)}const o=e.element.classList;this.it.forEach(e=>{e in t||(o.remove(e),this.it.delete(e))});for(const e in t){const n=!!t[e];n===this.it.has(e)||null!=(r=this.nt)&&r.has(e)||(n?(o.add(e),this.it.add(e)):(o.remove(e),this.it.delete(e)))}return _}});t="undefined"!=typeof navigator&&0<navigator.userAgent.toLowerCase().indexOf("firefox");function it(e,t,n){e.addEventListener?e.addEventListener(t,n,!1):e.attachEvent&&e.attachEvent("on".concat(t),function(){n(window.event)})}function at(e,t){for(var n=t.slice(0,t.length-1),r=0;r<n.length;r++)n[r]=e[n[r].toLowerCase()];return n}function st(e){for(var t=(e=(e="string"!=typeof e?"":e).replace(/\s/g,"")).split(","),n=t.lastIndexOf("");0<=n;)t[n-1]+=",",t.splice(n,1),n=t.lastIndexOf("");return t}for(var lt={backspace:8,tab:9,clear:12,enter:13,return:13,esc:27,escape:27,space:32,left:37,up:38,right:39,down:40,del:46,delete:46,ins:45,insert:45,home:36,end:35,pageup:33,pagedown:34,capslock:20,num_0:96,num_1:97,num_2:98,num_3:99,num_4:100,num_5:101,num_6:102,num_7:103,num_8:104,num_9:105,num_multiply:106,num_add:107,num_enter:108,num_subtract:109,num_decimal:110,num_divide:111,"⇪":20,",":188,".":190,"/":191,"`":192,"-":t?173:189,"=":t?61:187,";":t?59:186,"'":222,"[":219,"]":221,"\\":220},A={"⇧":16,shift:16,"⌥":18,alt:18,option:18,"⌃":17,ctrl:17,control:17,"⌘":91,cmd:91,command:91},ct={16:"shiftKey",18:"altKey",17:"ctrlKey",91:"metaKey",shiftKey:16,ctrlKey:17,altKey:18,metaKey:91},x={16:!1,18:!1,17:!1,91:!1},P={},ut=1;ut<20;ut++)lt["f".concat(ut)]=111+ut;var S=[],ht="all",dt=[],pt=function(e){return lt[e.toLowerCase()]||A[e.toLowerCase()]||e.toUpperCase().charCodeAt(0)};function ft(e){ht=e||"all"}function M(){return ht||"all"}function _t(e){var t=e.key,r=e.scope,o=e.method,a=void 0===(e=e.splitKey)?"+":e;st(t).forEach(function(e){var i,e=e.split(a),t=e.length,n=e[t-1],n="*"===n?"*":pt(n);P[n]&&(r=r||M(),i=1<t?at(A,e):[],P[n]=P[n].map(function(e){return o&&e.method!==o||e.scope!==r||!function(e){for(var t=e.length>=i.length?e:i,n=e.length>=i.length?i:e,r=!0,o=0;o<t.length;o++)-1===n.indexOf(t[o])&&(r=!1);return r}(e.mods)?e:{}}))})}function yt(e,t,n){var r;if(t.scope===n||"all"===t.scope){for(var o in r=0<t.mods.length,x)Object.prototype.hasOwnProperty.call(x,o)&&(!x[o]&&-1<t.mods.indexOf(+o)||x[o]&&-1===t.mods.indexOf(+o))&&(r=!1);(0!==t.mods.length||x[16]||x[18]||x[17]||x[91])&&!r&&"*"!==t.shortcut||!1===t.method(e,t)&&(e.preventDefault?e.preventDefault():e.returnValue=!1,e.stopPropagation&&e.stopPropagation(),e.cancelBubble)&&(e.cancelBubble=!0)}}function vt(n){var e=P["*"],t=n.keyCode||n.which||n.charCode;if(C.filter.call(this,n)){if(-1===S.indexOf(t=93!==t&&224!==t?t:91)&&229!==t&&S.push(t),["ctrlKey","altKey","shiftKey","metaKey"].forEach(function(e){var t=ct[e];n[e]&&-1===S.indexOf(t)?S.push(t):!n[e]&&-1<S.indexOf(t)?S.splice(S.indexOf(t),1):"metaKey"!==e||!n[e]||3!==S.length||n.ctrlKey||n.shiftKey||n.altKey||(S=S.slice(S.indexOf(t)))}),t in x){for(var r in x[t]=!0,A)A[r]===t&&(C[r]=!0);if(!e)return}for(var o in x)Object.prototype.hasOwnProperty.call(x,o)&&(x[o]=n[ct[o]]);n.getModifierState&&(!n.altKey||n.ctrlKey)&&n.getModifierState("AltGraph")&&(-1===S.indexOf(17)&&S.push(17),-1===S.indexOf(18)&&S.push(18),x[17]=!0,x[18]=!0);var i=M();if(e)for(var a=0;a<e.length;a++)e[a].scope===i&&("keydown"===n.type&&e[a].keydown||"keyup"===n.type&&e[a].keyup)&&yt(n,e[a],i);if(t in P)for(var s=0;s<P[t].length;s++)if(("keydown"===n.type&&P[t][s].keydown||"keyup"===n.type&&P[t][s].keyup)&&P[t][s].key){for(var l=P[t][s],c=l.splitKey,u=l.key.split(c),h=[],d=0;d<u.length;d++)h.push(pt(u[d]));h.sort().join("")===S.sort().join("")&&yt(n,l,i)}}}function C(e,t,n){S=[];var r=st(e),o=[],i="all",a=document,s=0,l=!1,c=!0,u="+";for(void 0===n&&"function"==typeof t&&(n=t),"[object Object]"===Object.prototype.toString.call(t)&&(t.scope&&(i=t.scope),t.element&&(a=t.element),t.keyup&&(l=t.keyup),void 0!==t.keydown&&(c=t.keydown),"string"==typeof t.splitKey)&&(u=t.splitKey),"string"==typeof t&&(i=t);s<r.length;s++)o=[],1<(e=r[s].split(u)).length&&(o=at(A,e)),(e="*"===(e=e[e.length-1])?"*":pt(e))in P||(P[e]=[]),P[e].push({keyup:l,keydown:c,scope:i,mods:o,shortcut:r[s],method:n,key:r[s],splitKey:u});void 0===a||(t=a,-1<dt.indexOf(t))||!window||(dt.push(a),it(a,"keydown",function(e){vt(e)}),it(window,"focus",function(){S=[]}),it(a,"keyup",function(e){vt(e);var t=e.keyCode||e.which||e.charCode,n=S.indexOf(t);if(0<=n&&S.splice(n,1),e.key&&"meta"===e.key.toLowerCase()&&S.splice(0,S.length),(t=93!==t&&224!==t?t:91)in x)for(var r in x[t]=!1,A)A[r]===t&&(C[r]=!1)}))}var mt,bt,gt={setScope:ft,getScope:M,deleteScope:function(e,t){var n,r,o;for(o in e=e||M(),P)if(Object.prototype.hasOwnProperty.call(P,o))for(n=P[o],r=0;r<n.length;)n[r].scope===e?n.splice(r,1):r++;M()===e&&ft(t||"all")},getPressedKeyCodes:function(){return S.slice(0)},isPressed:function(e){return"string"==typeof e&&(e=pt(e)),-1!==S.indexOf(e)},filter:function(e){var e=e.target||e.srcElement,t=e.tagName,n=!0;return n=!e.isContentEditable&&("INPUT"!==t&&"TEXTAREA"!==t&&"SELECT"!==t||e.readOnly)?n:!1},unbind:function(e){if(e){if(Array.isArray(e))e.forEach(function(e){e.key&&_t(e)});else if("object"==typeof e)e.key&&_t(e);else if("string"==typeof e){for(var t=arguments.length,n=new Array(1<t?t-1:0),r=1;r<t;r++)n[r-1]=arguments[r];var o=n[0],i=n[1];"function"==typeof o&&(i=o,o=""),_t({key:e,scope:o,method:i,splitKey:"+"})}}else Object.keys(P).forEach(function(e){return delete P[e]})}};for(mt in gt)Object.prototype.hasOwnProperty.call(gt,mt)&&(C[mt]=gt[mt]);"undefined"!=typeof window&&(bt=window.hotkeys,C.noConflict=function(e){return e&&window.hotkeys===C&&(window.hotkeys=bt),C},window.hotkeys=C);function D(e,t,n,r){var o,i=arguments.length,a=i<3?t:null===r?r=Object.getOwnPropertyDescriptor(t,n):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(e,t,n,r);else for(var s=e.length-1;0<=s;s--)(o=e[s])&&(a=(i<3?o(a):3<i?o(t,n,a):o(t,n))||a);return 3<i&&a&&Object.defineProperty(t,n,a),a}var L=C,r=class extends o{constructor(){super(...arguments),this.placeholder="",this.hideBreadcrumbs=!1,this.breadcrumbHome="Home",this.breadcrumbs=[],this._inputRef=et()}render(){let e="";if(!this.hideBreadcrumbs){var t=[];for(const e of this.breadcrumbs)t.push(i`<button
            tabindex="-1"
            @click=${()=>this.selectParent(e)}
            class="breadcrumb"
          >
            ${e}
          </button>`);e=i`<div class="breadcrumb-list">
        <button
          tabindex="-1"
          @click=${()=>this.selectParent()}
          class="breadcrumb"
        >
          ${this.breadcrumbHome}
        </button>
        ${t}
      </div>`}return i`
      ${e}
      <div part="ninja-input-wrapper" class="search-wrapper">
        <input
          part="ninja-input"
          type="text"
          id="search"
          spellcheck="false"
          autocomplete="off"
          @input="${this._handleInput}"
          ${rt(this._inputRef)}
          placeholder="${this.placeholder}"
          class="search"
        />
      </div>
    `}setSearch(e){this._inputRef.value&&(this._inputRef.value.value=e)}focusSearch(){requestAnimationFrame(()=>this._inputRef.value.focus())}_handleInput(e){e=e.target;this.dispatchEvent(new CustomEvent("change",{detail:{search:e.value},bubbles:!1,composed:!1}))}selectParent(e){this.dispatchEvent(new CustomEvent("setParent",{detail:{parent:e},bubbles:!0,composed:!0}))}firstUpdated(){this.focusSearch()}_close(){this.dispatchEvent(new CustomEvent("close",{bubbles:!0,composed:!0}))}};r.styles=K`
    :host {
      flex: 1;
      position: relative;
    }
    .search {
      padding: 1.25em;
      flex-grow: 1;
      flex-shrink: 0;
      margin: 0px;
      border: none;
      appearance: none;
      font-size: 1.125em;
      background: transparent;
      caret-color: var(--ninja-accent-color);
      color: var(--ninja-text-color);
      outline: none;
      font-family: var(--ninja-font-family);
    }
    .search::placeholder {
      color: var(--ninja-placeholder-color);
    }
    .breadcrumb-list {
      padding: 1em 4em 0 1em;
      display: flex;
      flex-direction: row;
      align-items: stretch;
      justify-content: flex-start;
      flex: initial;
    }

    .breadcrumb {
      background: var(--ninja-secondary-background-color);
      text-align: center;
      line-height: 1.2em;
      border-radius: var(--ninja-key-border-radius);
      border: 0;
      cursor: pointer;
      padding: 0.1em 0.5em;
      color: var(--ninja-secondary-text-color);
      margin-right: 0.5em;
      outline: none;
      font-family: var(--ninja-font-family);
    }

    .search-wrapper {
      display: flex;
      border-bottom: var(--ninja-separate-border);
    }
  `,D([a()],r.prototype,"placeholder",void 0),D([a({type:Boolean})],r.prototype,"hideBreadcrumbs",void 0),D([a()],r.prototype,"breadcrumbHome",void 0),D([a({type:Array})],r.prototype,"breadcrumbs",void 0),D([Ce("ninja-header")],r);class wt extends E{constructor(e){if(super(e),this.et=y,e.type!==Ie)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===y||null==e)return this.ft=void 0,this.et=e;if(e===_)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");return e===this.et?this.ft:(e=[this.et=e],this.ft={_$litType$:this.constructor.resultType,strings:e.raw=e,values:[]})}}wt.directiveName="unsafeHTML",wt.resultType=1;const Et=w(wt);function kt(e,t,n,r){var o,i=arguments.length,a=i<3?t:null===r?r=Object.getOwnPropertyDescriptor(t,n):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(e,t,n,r);else for(var s=e.length-1;0<=s;s--)(o=e[s])&&(a=(i<3?o(a):3<i?o(t,n,a):o(t,n))||a);return 3<i&&a&&Object.defineProperty(t,n,a),a}n=e(2),t=K`:host{font-family:var(--mdc-icon-font, "Material Icons");font-weight:normal;font-style:normal;font-size:var(--mdc-icon-size, 24px);line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;word-wrap:normal;direction:ltr;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;-moz-osx-font-smoothing:grayscale;font-feature-settings:"liga"}`,r=class extends o{render(){return i`<span><slot></slot></span>`}},r.styles=[t],Object(n.c)([Ce("mwc-icon")],r),e=class extends o{constructor(){super(),this.selected=!1,this.hotKeysJoinedView=!0,this.addEventListener("click",this.click)}ensureInView(){requestAnimationFrame(()=>this.scrollIntoView({block:"nearest"}))}click(){this.dispatchEvent(new CustomEvent("actionsSelected",{detail:this.action,bubbles:!0,composed:!0}))}updated(e){e.has("selected")&&this.selected&&this.ensureInView()}render(){let e,t;this.action.mdIcon?e=i`<mwc-icon part="ninja-icon" class="ninja-icon"
        >${this.action.mdIcon}</mwc-icon
      >`:this.action.icon&&(e=Et(this.action.icon||"")),this.action.hotkey&&(t=this.hotKeysJoinedView?this.action.hotkey.split(",").map(e=>{e=e.split("+"),e=i`${function*(t){if(void 0!==t){let e=-1;for(const n of t)-1<e&&(yield"+"),e++,yield n}}(e.map(e=>i`<kbd>${e}</kbd>`))}`;return i`<div class="ninja-hotkey ninja-hotkeys">
            ${e}
          </div>`}):this.action.hotkey.split(",").map(e=>{e=e.split("+").map(e=>i`<kbd class="ninja-hotkey">${e}</kbd>`);return i`<kbd class="ninja-hotkeys">${e}</kbd>`}));var n={selected:this.selected,"ninja-action":!0};return i`
      <div
        class="ninja-action"
        part="ninja-action ${this.selected?"ninja-selected":""}"
        class=${ot(n)}
      >
        ${e}
        <div class="ninja-title">${this.action.title}</div>
        ${t}
      </div>
    `}};e.styles=K`
    :host {
      display: flex;
      width: 100%;
    }
    .ninja-action {
      padding: 0.75em 1em;
      display: flex;
      border-left: 2px solid transparent;
      align-items: center;
      justify-content: start;
      outline: none;
      transition: color 0s ease 0s;
      width: 100%;
    }
    .ninja-action.selected {
      cursor: pointer;
      color: var(--ninja-selected-text-color);
      background-color: var(--ninja-selected-background);
      border-left: 2px solid var(--ninja-accent-color);
      outline: none;
    }
    .ninja-action.selected .ninja-icon {
      color: var(--ninja-selected-text-color);
    }
    .ninja-icon {
      font-size: var(--ninja-icon-size);
      max-width: var(--ninja-icon-size);
      max-height: var(--ninja-icon-size);
      margin-right: 1em;
      color: var(--ninja-icon-color);
      margin-right: 1em;
      position: relative;
    }

    .ninja-title {
      flex-shrink: 0.01;
      margin-right: 0.5em;
      flex-grow: 1;
      font-size: 0.8125em;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .ninja-hotkeys {
      flex-shrink: 0;
      width: min-content;
      display: flex;
    }

    .ninja-hotkeys kbd {
      font-family: inherit;
    }
    .ninja-hotkey {
      background: var(--ninja-secondary-background-color);
      padding: 0.06em 0.25em;
      border-radius: var(--ninja-key-border-radius);
      text-transform: capitalize;
      color: var(--ninja-secondary-text-color);
      font-size: 0.75em;
      font-family: inherit;
    }

    .ninja-hotkey + .ninja-hotkey {
      margin-left: 0.5em;
    }
    .ninja-hotkeys + .ninja-hotkeys {
      margin-left: 1em;
    }
  `,kt([a({type:Object})],e.prototype,"action",void 0),kt([a({type:Boolean})],e.prototype,"selected",void 0),kt([a({type:Boolean})],e.prototype,"hotKeysJoinedView",void 0),kt([Ce("ninja-action")],e);const $t=i` <div class="modal-footer" slot="footer">
  <span class="help">
    <svg
      version="1.0"
      class="ninja-examplekey"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1280 1280"
    >
      <path
        d="M1013 376c0 73.4-.4 113.3-1.1 120.2a159.9 159.9 0 0 1-90.2 127.3c-20 9.6-36.7 14-59.2 15.5-7.1.5-121.9.9-255 1h-242l95.5-95.5 95.5-95.5-38.3-38.2-38.2-38.3-160 160c-88 88-160 160.4-160 161 0 .6 72 73 160 161l160 160 38.2-38.3 38.3-38.2-95.5-95.5-95.5-95.5h251.1c252.9 0 259.8-.1 281.4-3.6 72.1-11.8 136.9-54.1 178.5-116.4 8.6-12.9 22.6-40.5 28-55.4 4.4-12 10.7-36.1 13.1-50.6 1.6-9.6 1.8-21 2.1-132.8l.4-122.2H1013v110z"
      />
    </svg>

    to select
  </span>
  <span class="help">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="ninja-examplekey"
      viewBox="0 0 24 24"
    >
      <path d="M0 0h24v24H0V0z" fill="none" />
      <path
        d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"
      />
    </svg>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="ninja-examplekey"
      viewBox="0 0 24 24"
    >
      <path d="M0 0h24v24H0V0z" fill="none" />
      <path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z" />
    </svg>
    to navigate
  </span>
  <span class="help">
    <span class="ninja-examplekey esc">esc</span>
    to close
  </span>
  <span class="help">
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="ninja-examplekey backspace"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        fill-rule="evenodd"
        d="M6.707 4.879A3 3 0 018.828 4H15a3 3 0 013 3v6a3 3 0 01-3 3H8.828a3 3 0 01-2.12-.879l-4.415-4.414a1 1 0 010-1.414l4.414-4.414zm4 2.414a1 1 0 00-1.414 1.414L10.586 10l-1.293 1.293a1 1 0 101.414 1.414L12 11.414l1.293 1.293a1 1 0 001.414-1.414L13.414 10l1.293-1.293a1 1 0 00-1.414-1.414L12 8.586l-1.293-1.293z"
        clip-rule="evenodd"
      />
    </svg>
    move to parent
  </span>
</div>`,jt=K`
  :host {
    --ninja-width: 640px;
    --ninja-backdrop-filter: none;
    --ninja-overflow-background: rgba(255, 255, 255, 0.5);
    --ninja-text-color: rgb(60, 65, 73);
    --ninja-font-size: 16px;
    --ninja-top: 20%;

    --ninja-key-border-radius: 0.25em;
    --ninja-accent-color: rgb(110, 94, 210);
    --ninja-secondary-background-color: rgb(239, 241, 244);
    --ninja-secondary-text-color: rgb(107, 111, 118);

    --ninja-selected-background: rgb(248, 249, 251);

    --ninja-icon-color: var(--ninja-secondary-text-color);
    --ninja-icon-size: 1.2em;
    --ninja-separate-border: 1px solid var(--ninja-secondary-background-color);

    --ninja-modal-background: #fff;
    --ninja-modal-shadow: rgb(0 0 0 / 50%) 0px 16px 70px;

    --ninja-actions-height: 300px;
    --ninja-group-text-color: rgb(144, 149, 157);

    --ninja-footer-background: rgba(242, 242, 242, 0.4);

    --ninja-placeholder-color: #8e8e8e;

    font-size: var(--ninja-font-size);

    --ninja-z-index: 1;
  }

  :host(.dark) {
    --ninja-backdrop-filter: none;
    --ninja-overflow-background: rgba(0, 0, 0, 0.7);
    --ninja-text-color: #7d7d7d;

    --ninja-modal-background: rgba(17, 17, 17, 0.85);
    --ninja-accent-color: rgb(110, 94, 210);
    --ninja-secondary-background-color: rgba(51, 51, 51, 0.44);
    --ninja-secondary-text-color: #888;

    --ninja-selected-text-color: #eaeaea;
    --ninja-selected-background: rgba(51, 51, 51, 0.44);

    --ninja-icon-color: var(--ninja-secondary-text-color);
    --ninja-separate-border: 1px solid var(--ninja-secondary-background-color);

    --ninja-modal-shadow: 0 16px 70px rgba(0, 0, 0, 0.2);

    --ninja-group-text-color: rgb(144, 149, 157);

    --ninja-footer-background: rgba(30, 30, 30, 85%);
  }

  .modal {
    display: none;
    position: fixed;
    z-index: var(--ninja-z-index);
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background: var(--ninja-overflow-background);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    -webkit-backdrop-filter: var(--ninja-backdrop-filter);
    backdrop-filter: var(--ninja-backdrop-filter);
    text-align: left;
    color: var(--ninja-text-color);
    font-family: var(--ninja-font-family);
  }
  .modal.visible {
    display: block;
  }

  .modal-content {
    position: relative;
    top: var(--ninja-top);
    margin: auto;
    padding: 0;
    display: flex;
    flex-direction: column;
    flex-shrink: 1;
    -webkit-box-flex: 1;
    flex-grow: 1;
    min-width: 0px;
    will-change: transform;
    background: var(--ninja-modal-background);
    border-radius: 0.5em;
    box-shadow: var(--ninja-modal-shadow);
    max-width: var(--ninja-width);
    overflow: hidden;
  }

  .bump {
    animation: zoom-in-zoom-out 0.2s ease;
  }

  @keyframes zoom-in-zoom-out {
    0% {
      transform: scale(0.99);
    }
    50% {
      transform: scale(1.01, 1.01);
    }
    100% {
      transform: scale(1, 1);
    }
  }

  .ninja-github {
    color: var(--ninja-keys-text-color);
    font-weight: normal;
    text-decoration: none;
  }

  .actions-list {
    max-height: var(--ninja-actions-height);
    overflow: auto;
    scroll-behavior: smooth;
    position: relative;
    margin: 0;
    padding: 0.5em 0;
    list-style: none;
    scroll-behavior: smooth;
  }

  .group-header {
    height: 1.375em;
    line-height: 1.375em;
    padding-left: 1.25em;
    padding-top: 0.5em;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    font-size: 0.75em;
    line-height: 1em;
    color: var(--ninja-group-text-color);
    margin: 1px 0;
  }

  .modal-footer {
    background: var(--ninja-footer-background);
    padding: 0.5em 1em;
    display: flex;
    /* font-size: 0.75em; */
    border-top: var(--ninja-separate-border);
    color: var(--ninja-secondary-text-color);
  }

  .modal-footer .help {
    display: flex;
    margin-right: 1em;
    align-items: center;
    font-size: 0.75em;
  }

  .ninja-examplekey {
    background: var(--ninja-secondary-background-color);
    padding: 0.06em 0.25em;
    border-radius: var(--ninja-key-border-radius);
    color: var(--ninja-secondary-text-color);
    width: 1em;
    height: 1em;
    margin-right: 0.5em;
    font-size: 1.25em;
    fill: currentColor;
  }
  .ninja-examplekey.esc {
    width: auto;
    height: auto;
    font-size: 1.1em;
  }
  .ninja-examplekey.backspace {
    opacity: 0.7;
  }
`;function T(e,t,n,r){var o,i=arguments.length,a=i<3?t:null===r?r=Object.getOwnPropertyDescriptor(t,n):r;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)a=Reflect.decorate(e,t,n,r);else for(var s=e.length-1;0<=s;s--)(o=e[s])&&(a=(i<3?o(a):3<i?o(t,n,a):o(t,n))||a);return 3<i&&a&&Object.defineProperty(t,n,a),a}t=class extends o{constructor(){super(...arguments),this.placeholder="Type a command or search...",this.disableHotkeys=!1,this.hideBreadcrumbs=!1,this.openHotkey="cmd+k,ctrl+k",this.navigationUpHotkey="up,shift+tab",this.navigationDownHotkey="down,tab",this.closeHotkey="esc",this.goBackHotkey="backspace",this.selectHotkey="enter",this.hotKeysJoinedView=!1,this.noAutoLoadMdIcons=!1,this.data=[],this.visible=!1,this._bump=!0,this._actionMatches=[],this._search="",this._flatData=[],this._headerRef=et()}open(e={}){this._bump=!0,this.visible=!0,this._headerRef.value.focusSearch(),0<this._actionMatches.length&&(this._selected=this._actionMatches[0]),this.setParent(e.parent)}close(){this._bump=!1,this.visible=!1}setParent(e){this._currentRoot=e||void 0,this._selected=void 0,this._search="",this._headerRef.value.setSearch("")}get breadcrumbs(){var e,t=[];let n=null==(e=this._selected)?void 0:e.parent;if(n)for(t.push(n);n;){const e=this._flatData.find(e=>e.id===n);null!=e&&e.parent&&t.push(e.parent),n=e?e.parent:void 0}return t.reverse()}connectedCallback(){super.connectedCallback(),this.noAutoLoadMdIcons||document.fonts.load("24px Material Icons","apps").then(()=>{}),this._registerInternalHotkeys()}disconnectedCallback(){super.disconnectedCallback(),this._unregisterInternalHotkeys()}_flattern(e,r){let o=[];return(e=e||[]).map(e=>{var t=e.children&&e.children.some(e=>"string"==typeof e),n={...e,parent:e.parent||r};return t||(n.children&&n.children.length&&(r=e.id,o=[...o,...n.children]),n.children=n.children?n.children.map(e=>e.id):[]),n}).concat(o.length?this._flattern(o,r):o)}update(e){e.has("data")&&!this.disableHotkeys&&(this._flatData=this._flattern(this.data),this._flatData.filter(e=>!!e.hotkey).forEach(t=>{L(t.hotkey,e=>{e.preventDefault(),t.handler&&t.handler(t)})})),super.update(e)}_registerInternalHotkeys(){this.openHotkey&&L(this.openHotkey,e=>{e.preventDefault(),this.visible?this.close():this.open()}),this.selectHotkey&&L(this.selectHotkey,e=>{this.visible&&(e.preventDefault(),this._actionSelected(this._actionMatches[this._selectedIndex]))}),this.goBackHotkey&&L(this.goBackHotkey,e=>{!this.visible||this._search||(e.preventDefault(),this._goBack())}),this.navigationDownHotkey&&L(this.navigationDownHotkey,e=>{this.visible&&(e.preventDefault(),this._selectedIndex>=this._actionMatches.length-1?this._selected=this._actionMatches[0]:this._selected=this._actionMatches[this._selectedIndex+1])}),this.navigationUpHotkey&&L(this.navigationUpHotkey,e=>{this.visible&&(e.preventDefault(),0===this._selectedIndex?this._selected=this._actionMatches[this._actionMatches.length-1]:this._selected=this._actionMatches[this._selectedIndex-1])}),this.closeHotkey&&L(this.closeHotkey,()=>{this.visible&&this.close()})}_unregisterInternalHotkeys(){this.openHotkey&&L.unbind(this.openHotkey),this.selectHotkey&&L.unbind(this.selectHotkey),this.goBackHotkey&&L.unbind(this.goBackHotkey),this.navigationDownHotkey&&L.unbind(this.navigationDownHotkey),this.navigationUpHotkey&&L.unbind(this.navigationUpHotkey),this.closeHotkey&&L.unbind(this.closeHotkey)}_actionFocused(e,t){this._selected=e,t.target.ensureInView()}_onTransitionEnd(){this._bump=!1}_goBack(){var e=1<this.breadcrumbs.length?this.breadcrumbs[this.breadcrumbs.length-2]:void 0;this.setParent(e)}render(){var e={bump:this._bump,"modal-content":!0},t={visible:this.visible,modal:!0},n=this._flatData.filter(e=>{var t=new RegExp(this._search,"gi"),n=e.title.match(t)||(null==(n=e.keywords)?void 0:n.match(t));return(!this._currentRoot&&this._search||e.parent===this._currentRoot)&&n}).reduce((e,t)=>e.set(t.section,[...e.get(t.section)||[],t]),new Map);this._actionMatches=[...n.values()].flat(),0<this._actionMatches.length&&-1===this._selectedIndex&&(this._selected=this._actionMatches[0]),0===this._actionMatches.length&&(this._selected=void 0);const r=e=>i` ${Ge(e,e=>e.id,t=>{var e;return i`<ninja-action
            exportparts="ninja-action,ninja-selected,ninja-icon"
            .selected=${qe(t.id===(null==(e=this._selected)?void 0:e.id))}
            .hotKeysJoinedView=${this.hotKeysJoinedView}
            @mouseover=${e=>this._actionFocused(t,e)}
            @actionsSelected=${e=>this._actionSelected(e.detail)}
            .action=${t}
          ></ninja-action>`})}`,o=[];return n.forEach((e,t)=>{t=t?i`<div class="group-header">${t}</div>`:void 0;o.push(i`${t}${r(e)}`)}),i`
      <div @click=${this._overlayClick} class=${ot(t)}>
        <div class=${ot(e)} @animationend=${this._onTransitionEnd}>
          <ninja-header
            exportparts="ninja-input,ninja-input-wrapper"
            ${rt(this._headerRef)}
            .placeholder=${this.placeholder}
            .hideBreadcrumbs=${this.hideBreadcrumbs}
            .breadcrumbs=${this.breadcrumbs}
            @change=${this._handleInput}
            @setParent=${e=>this.setParent(e.detail.parent)}
            @close=${this.close}
          >
          </ninja-header>
          <div class="modal-body">
            <div class="actions-list" part="actions-list">${o}</div>
          </div>
          <slot name="footer"> ${$t} </slot>
        </div>
      </div>
    `}get _selectedIndex(){return this._selected?this._actionMatches.indexOf(this._selected):-1}_actionSelected(e){var t;if(this.dispatchEvent(new CustomEvent("selected",{detail:{search:this._search,action:e},bubbles:!0,composed:!0})),e){if(e.children&&0<(null==(t=e.children)?void 0:t.length)&&(this._currentRoot=e.id,this._search=""),this._headerRef.value.setSearch(""),this._headerRef.value.focusSearch(),e.handler){const t=e.handler(e);null!=t&&t.keepOpen||this.close()}this._bump=!0}}async _handleInput(e){this._search=e.detail.search,await this.updateComplete,this.dispatchEvent(new CustomEvent("change",{detail:{search:this._search,actions:this._actionMatches},bubbles:!0,composed:!0}))}_overlayClick(e){null!=(e=e.target)&&e.classList.contains("modal")&&this.close()}};t.styles=[jt],T([a({type:String})],t.prototype,"placeholder",void 0),T([a({type:Boolean})],t.prototype,"disableHotkeys",void 0),T([a({type:Boolean})],t.prototype,"hideBreadcrumbs",void 0),T([a()],t.prototype,"openHotkey",void 0),T([a()],t.prototype,"navigationUpHotkey",void 0),T([a()],t.prototype,"navigationDownHotkey",void 0),T([a()],t.prototype,"closeHotkey",void 0),T([a()],t.prototype,"goBackHotkey",void 0),T([a()],t.prototype,"selectHotkey",void 0),T([a({type:Boolean})],t.prototype,"hotKeysJoinedView",void 0),T([a({type:Boolean})],t.prototype,"noAutoLoadMdIcons",void 0),T([a({type:Array,hasChanged:()=>!0})],t.prototype,"data",void 0),T([s()],t.prototype,"visible",void 0),T([s()],t.prototype,"_bump",void 0),T([s()],t.prototype,"_actionMatches",void 0),T([s()],t.prototype,"_search",void 0),T([s()],t.prototype,"_currentRoot",void 0),T([s()],t.prototype,"_flatData",void 0),T([s()],t.prototype,"breadcrumbs",null),T([s()],t.prototype,"_selected",void 0),T([Ce("ninja-keys")],t)}}]);