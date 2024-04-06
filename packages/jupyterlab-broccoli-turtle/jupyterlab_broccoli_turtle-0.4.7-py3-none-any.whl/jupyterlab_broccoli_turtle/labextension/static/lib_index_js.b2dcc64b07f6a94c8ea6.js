(self["webpackChunkjupyterlab_broccoli_turtle"] = self["webpackChunkjupyterlab_broccoli_turtle"] || []).push([["lib_index_js"],{

/***/ "./lib/msg lazy recursive ^\\.\\/.*\\.js$":
/*!*****************************************************!*\
  !*** ./lib/msg/ lazy ^\.\/.*\.js$ namespace object ***!
  \*****************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var map = {
	"./En.js": [
		"./lib/msg/En.js",
		"lib_msg_En_js"
	],
	"./Jp.js": [
		"./lib/msg/Jp.js",
		"lib_msg_Jp_js"
	]
};
function webpackAsyncContext(req) {
	if(!__webpack_require__.o(map, req)) {
		return Promise.resolve().then(() => {
			var e = new Error("Cannot find module '" + req + "'");
			e.code = 'MODULE_NOT_FOUND';
			throw e;
		});
	}

	var ids = map[req], id = ids[0];
	return __webpack_require__.e(ids[1]).then(() => {
		return __webpack_require__(id);
	});
}
webpackAsyncContext.keys = () => (Object.keys(map));
webpackAsyncContext.id = "./lib/msg lazy recursive ^\\.\\/.*\\.js$";
module.exports = webpackAsyncContext;

/***/ }),

/***/ "./lib/blocks.js":
/*!***********************!*\
  !*** ./lib/blocks.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TOOLBOX: () => (/* binding */ TOOLBOX)
/* harmony export */ });
/* harmony import */ var blockly__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! blockly */ "webpack/sharing/consume/default/blockly/blockly");
/* harmony import */ var blockly__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(blockly__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");
/* harmony import */ var _toolbox_basic__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./toolbox_basic */ "./lib/toolbox_basic.js");
/* harmony import */ var _toolbox_turtle__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./toolbox_turtle */ "./lib/toolbox_turtle.js");




//
const toolboxUtils = new _utils__WEBPACK_IMPORTED_MODULE_1__.ToolboxUtils();
const TOOLBOX = toolboxUtils.add(_toolbox_turtle__WEBPACK_IMPORTED_MODULE_2__.TOOLBOX_TURTLE, _toolbox_basic__WEBPACK_IMPORTED_MODULE_3__.TOOLBOX_BASIC, 2);
// Init
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_init',
        'message0': '%{BKY_BLOCK_TURTLE_INIT}  %1 %{BKY_BLOCK_TURTLE_XSIZE}  %2 %{BKY_BLOCK_TURTLE_YSIZE}  %3',
        'args0': [
            {
                'type': 'input_dummy'
            },
            {
                'type': 'input_value',
                'name': 'XSIZE',
                'check': 'Number',
                'align': 'RIGHT'
            },
            {
                'type': 'input_value',
                'name': 'YSIZE',
                'check': 'Number',
                'align': 'RIGHT'
            }
        ],
        'nextStatement': null,
        'colour': 5,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Turtle Speed
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_speed',
        'message0': '%{BKY_BLOCK_TURTLE_SPEED}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Number'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 290,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Line Width
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_line_width',
        'message0': '%{BKY_BLOCK_TURTLE_WIDTH}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Number'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 290,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Line Color
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_line_color',
        'message0': '%{BKY_BLOCK_TURTLE_COLOR}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Colour'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 290,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Line HSV Color
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_line_hsv',
        'message0': '%{BKY_BLOCK_TURTLE_HSV} %1' +
            '%{BKY_BLOCK_TURTLE_HSV_S}  %2' +
            '%{BKY_BLOCK_TURTLE_HSV_V}  %3',
        'args0': [
            {
                'type': 'input_value',
                'name': 'H',
                'check': 'Number',
                'align': 'RIGHT',
            },
            {
                'type': 'input_value',
                'name': 'S',
                'check': 'Number',
                'align': 'RIGHT',
            },
            {
                'type': 'input_value',
                'name': 'V',
                'check': 'Number',
                'align': 'RIGHT',
            },
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 290,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Pen Up
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_pen_up',
        'message0': '%{BKY_BLOCK_TURTLE_PEN_UP}',
        'previousStatement': null,
        'nextStatement': null,
        'colour': 50,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Pen Down
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_pen_down',
        'message0': '%{BKY_BLOCK_TURTLE_PEN_DOWN}',
        'previousStatement': null,
        'nextStatement': null,
        'colour': 50,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Foward
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_forward',
        'message0': '%{BKY_BLOCK_TURTLE_FORWARD}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Number'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 200,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Turn Right
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_turn_right',
        'message0': '%{BKY_BLOCK_TURTLE_TURN_RIGHT}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Number'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 200,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Turn Left
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_turn_left',
        'message0': '%{BKY_BLOCK_TURTLE_TURN_LEFT}  %1',
        'args0': [
            {
                'type': 'input_value',
                'name': 'VAL',
                'check': 'Number'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 200,
        'tooltip': '',
        'helpUrl': ''
    }]);
// Move to
blockly__WEBPACK_IMPORTED_MODULE_0__.defineBlocksWithJsonArray([{
        'type': 'turtle_move',
        'message0': '%{BKY_BLOCK_TURTLE_MOVE}  %1 %{BKY_BLOCK_TURTLE_XPOS}  %2 %{BKY_BLOCK_TURTLE_YPOS}  %3',
        'args0': [
            {
                'type': 'input_dummy'
            },
            {
                'type': 'input_value',
                'name': 'XPOS',
                'check': 'Number',
                'align': 'RIGHT'
            },
            {
                'type': 'input_value',
                'name': 'YPOS',
                'check': 'Number',
                'align': 'RIGHT'
            }
        ],
        'previousStatement': null,
        'nextStatement': null,
        'colour': 200,
        'tooltip': '',
        'helpUrl': ''
    }]);


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var jupyterlab_broccoli__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jupyterlab-broccoli */ "webpack/sharing/consume/default/jupyterlab-broccoli/jupyterlab-broccoli");
/* harmony import */ var jupyterlab_broccoli__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jupyterlab_broccoli__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _blocks__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./blocks */ "./lib/blocks.js");
/* harmony import */ var _python_func__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./python/func */ "./lib/python/func.js");
/* harmony import */ var _javascript_func_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./javascript/func.js */ "./lib/javascript/func.js");





//import { getLuaFunctions } from './lua/func.js';
//import { getDartFunctions } from './dart/func.js';
//import { getPHPFunctions } from './php/func.js';
/**
 * Initialization data for the jupyterlab-broccoli-turtle extension.
 */
const plugin = {
    id: 'jupyterlab-broccoli-turtle:plugin',
    autoStart: true,
    requires: [jupyterlab_broccoli__WEBPACK_IMPORTED_MODULE_0__.IBlocklyRegistry, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.ITranslator],
    activate: (app, register, translator) => {
        console.log('JupyterLab extension jupyterlab-broccoli-turtle is activated!');
        const bregister = register;
        // Localization 
        const language = bregister.language;
        __webpack_require__("./lib/msg lazy recursive ^\\.\\/.*\\.js$")(`./${language}.js`)
            .catch(() => {
            if (language !== 'En') {
                __webpack_require__.e(/*! import() */ "lib_msg_En_js").then(__webpack_require__.bind(__webpack_require__, /*! ./msg/En.js */ "./lib/msg/En.js"))
                    .catch(() => { });
            }
        });
        const trans = (translator || _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_1__.nullTranslator).load('jupyterlab');
        bregister.registerToolbox(trans.__('Turtle'), _blocks__WEBPACK_IMPORTED_MODULE_2__.TOOLBOX);
        const fpython = (0,_python_func__WEBPACK_IMPORTED_MODULE_3__.getPythonFunctions)(bregister.generators.get('python'));
        const fjavascript = (0,_javascript_func_js__WEBPACK_IMPORTED_MODULE_4__.getJsFunctions)(bregister.generators.get('javascript'));
        //const fphp = getPHPFunctions(bregister.generators.get('php'));
        //const flua = getLuaFunctions(bregister.generators.get('lua'));
        //const fdart = getDartFunctions(bregister.generators.get('dart'));
        //while (bregister.lock) {};
        //bregister.lock = true;
        // @ts-ignore
        bregister.registerCodes('python', fpython);
        // @ts-ignore
        bregister.registerCodes('javascript', fjavascript);
        // @ts-ignore
        //bregister.registerCodes('php', fphp);
        // @ts-ignore
        //bregister.registerCodes('lua', flua);
        // @ts-ignore
        //bregister.registerCodes('dart', fdart);
        //bregister.lock = false;
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/javascript/func.js":
/*!********************************!*\
  !*** ./lib/javascript/func.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getJsFunctions: () => (/* binding */ getJsFunctions)
/* harmony export */ });
//
//
//import { javascriptGenerator as Js } from 'blockly/javascript';
const notImplementedMsg = 'Not implemented at this Kernel';
function getJsFunctions(generator) {
    var funcs = {};
    //
    funcs['turtle_init'] = function (block) {
        alert(notImplementedMsg);
        return 'console.log(' + notImplementedMsg + ');\n';
    };
    //
    return funcs;
}


/***/ }),

/***/ "./lib/python/func.js":
/*!****************************!*\
  !*** ./lib/python/func.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   getPythonFunctions: () => (/* binding */ getPythonFunctions)
/* harmony export */ });
/* harmony import */ var blockly_python__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! blockly/python */ "./node_modules/blockly/python.js");
/* harmony import */ var blockly_python__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(blockly_python__WEBPACK_IMPORTED_MODULE_0__);

function getPythonFunctions(generator) {
    var funcs = {};
    //
    funcs['turtle_init'] = function (block) {
        const xsz = generator.valueToCode(block, 'XSIZE', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "600";
        const ysz = generator.valueToCode(block, 'YSIZE', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "600";
        const msg = 'from jbturtle import *\n' +
            'from math import * \n\n' +
            'turtle = JBTurtle(' + xsz + ', ' + ysz + ')\n';
        return msg;
    };
    funcs['turtle_speed'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "2";
        return 'turtle.speed(' + val + ')\n';
    };
    funcs['turtle_line_width'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "2";
        return 'turtle.line_width(' + val + ')\n';
    };
    funcs['turtle_line_color'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "#000000";
        return 'turtle.line_color(' + val + ')\n';
    };
    funcs['turtle_line_hsv'] = function (block) {
        const hh = generator.valueToCode(block, 'H', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "0";
        const ss = generator.valueToCode(block, 'S', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "0.45";
        const vv = generator.valueToCode(block, 'V', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "0.65";
        return 'turtle.line_hsv(' + hh + ', ' + ss + ', ' + vv + ')\n';
    };
    funcs['turtle_pen_up'] = function (block) {
        return 'turtle.pen_up()\n';
    };
    funcs['turtle_pen_down'] = function (block) {
        return 'turtle.pen_down()\n';
    };
    funcs['turtle_forward'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "100";
        return 'turtle.forward(' + val + ')\n';
    };
    funcs['turtle_turn_right'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "90";
        return 'turtle.turn_right(' + val + ')\n';
    };
    funcs['turtle_turn_left'] = function (block) {
        const val = generator.valueToCode(block, 'VAL', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "90";
        return 'turtle.turn_left(' + val + ')\n';
    };
    funcs['turtle_move'] = function (block) {
        const xp = generator.valueToCode(block, 'XPOS', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "300";
        const yp = generator.valueToCode(block, 'YPOS', blockly_python__WEBPACK_IMPORTED_MODULE_0__.pythonGenerator.ORDER_NONE) || "300";
        return 'turtle.move(' + xp + ', ' + yp + ')\n';
    };
    //
    return funcs;
}


/***/ }),

/***/ "./lib/toolbox_basic.js":
/*!******************************!*\
  !*** ./lib/toolbox_basic.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TOOLBOX_BASIC: () => (/* binding */ TOOLBOX_BASIC)
/* harmony export */ });
//
const TOOLBOX_BASIC = {
    kind: 'categoryToolbox',
    contents: [
        {
            kind: 'category',
            name: '%{BKY_TOOLBOX_LOGIC}',
            colour: '210',
            contents: [
                {
                    kind: 'block',
                    type: 'controls_if'
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_compare'
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_operation',
                    blockxml: `<block type='logic_operation'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_negate',
                    blockxml: `<block type='logic_negate'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_boolean',
                    blockxml: `<block type='logic_boolean'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_null',
                    blockxml: `<block type='logic_null'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'logic_ternary',
                    blockxml: `<block type='logic_ternary'></block>`
                }
            ]
        },
        {
            kind: 'category',
            name: '%{BKY_TOOLBOX_LOOPS}',
            colour: '120',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'controls_repeat_ext',
                    blockxml: `<block type='controls_repeat_ext'>
               <value name='TIMES'>
                 <shadow type='math_number'>
                   <field name='NUM'>10</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'controls_whileUntil',
                    blockxml: `<block type='controls_whileUntil'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'controls_for',
                    blockxml: `<block type='controls_for'>
               <value name='FROM'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
               <value name='TO'>
                 <shadow type='math_number'>
                   <field name='NUM'>10</field>
                 </shadow>
               </value>
               <value name='BY'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'controls_forEach',
                    blockxml: `<block type='controls_forEach'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'controls_flow_statements',
                    blockxml: `<block type='controls_flow_statements'></block>`
                }
            ]
        },
        {
            kind: 'CATEGORY',
            name: '%{BKY_TOOLBOX_MATH}',
            colour: '230',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'math_number',
                    blockxml: `<block type='math_number'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_arithmetic',
                    blockxml: `<block type='math_arithmetic'>
               <value name='A'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
               <value name='B'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_single',
                    blockxml: `<block type='math_single'>
               <value name='NUM'>
                 <shadow type='math_number'>
                   <field name='NUM'>9</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_trig',
                    blockxml: `<block type='math_trig'>
               <value name='NUM'>
                 <shadow type='math_number'>
                   <field name='NUM'>45</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_constant',
                    blockxml: `<block type='math_constant'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_number_property',
                    blockxml: `<block type='math_number_property'>
               <value name='NUMBER_TO_CHECK'>
                 <shadow type='math_number'>
                   <field name='NUM'>0</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_change',
                    blockxml: `<block type='math_change'>
               <value name='DELTA'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_round',
                    blockxml: `<block type='math_round'>
               <value name='NUM'>
                 <shadow type='math_number'>
                   <field name='NUM'>3.1</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_on_list',
                    blockxml: `<block type='math_on_list'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_modulo',
                    blockxml: `<block type='math_modulo'>
               <value name='DIVIDEND'>
                 <shadow type='math_number'>
                   <field name='NUM'>64</field>
                 </shadow>
               </value>
               <value name='DIVISOR'>
                 <shadow type='math_number'>
                   <field name='NUM'>10</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_constrain',
                    blockxml: `<block type='math_constrain'>
              <value name='VALUE'>
                <shadow type='math_number'>
                  <field name='NUM'>50</field>
                </shadow>
              </value>
              <value name='LOW'>
                <shadow type='math_number'>
                  <field name='NUM'>1</field>
                </shadow>
              </value>
              <value name='HIGH'>
                <shadow type='math_number'>
                  <field name='NUM'>100</field>
                </shadow>
              </value>
            </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_random_int',
                    blockxml: `<block type='math_random_int'>
               <value name='FROM'>
                 <shadow type='math_number'>
                   <field name='NUM'>1</field>
                 </shadow>
               </value>
               <value name='TO'>
                 <shadow type='math_number'>
                   <field name='NUM'>100</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'math_random_float',
                    blockxml: `<block type='math_random_float'></block>`
                }
            ]
        },
        {
            kind: 'CATEGORY',
            name: '%{BKY_TOOLBOX_TEXT}',
            colour: '160',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'text',
                    blockxml: `<block type='text'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_join',
                    blockxml: `<block type='text_join'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_append',
                    blockxml: `<block type='text_append'>
               <value name='TEXT'>
                 <shadow type='text'></shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_length',
                    blockxml: `<block type='text_length'>
               <value name='VALUE'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_isEmpty',
                    blockxml: `<block type='text_isEmpty'>
               <value name='VALUE'>
                 <shadow type='text'>
                   <field name='TEXT'></field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_indexOf',
                    blockxml: `<block type='text_indexOf'>
               <value name='VALUE'>
                 <block type='variables_get'>
                   <field name='VAR'>text</field>
                 </block>
               </value>
               <value name='FIND'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_charAt',
                    blockxml: `<block type='text_charAt'>
               <value name='VALUE'>
                 <block type='variables_get'>
                   <field name='VAR'>text</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_getSubstring',
                    blockxml: `<block type='text_getSubstring'>
               <value name='STRING'>
                 <block type='variables_get'>
                   <field name='VAR'>text</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_changeCase',
                    blockxml: `<block type='text_changeCase'>
               <value name='TEXT'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_trim',
                    blockxml: `<block type='text_trim'>
               <value name='TEXT'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_print',
                    blockxml: `<block type='text_print'>
               <value name='TEXT'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'text_prompt_ext',
                    blockxml: `<block type='text_prompt_ext'>
               <value name='TEXT'>
                 <shadow type='text'>
                   <field name='TEXT'>abc</field>
                 </shadow>
               </value>
             </block>`
                }
            ]
        },
        {
            kind: 'CATEGORY',
            name: '%{BKY_TOOLBOX_LISTS}',
            colour: '260',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'lists_create_with',
                    blockxml: `<block type='lists_create_with'>
               <mutation items='0'></mutation>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_create_with',
                    blockxml: `<block type='lists_create_with'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_repeat',
                    blockxml: `<block type='lists_repeat'>
               <value name='NUM'>
                 <shadow type='math_number'>
                   <field name='NUM'>5</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_length',
                    blockxml: `<block type='lists_length'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_isEmpty',
                    blockxml: `<block type='lists_isEmpty'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_indexOf',
                    blockxml: `<block type='lists_indexOf'>
               <value name='VALUE'>
                 <block type='variables_get'>
                   <field name='VAR'>list</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_getIndex',
                    blockxml: `<block type='lists_getIndex'>
               <value name='VALUE'>
                 <block type='variables_get'>
                   <field name='VAR'>list</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_setIndex',
                    blockxml: `<block type='lists_setIndex'>
               <value name='LIST'>
                 <block type='variables_get'>
                   <field name='VAR'>list</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_getSublist',
                    blockxml: `<block type='lists_getSublist'>
               <value name='LIST'>
                 <block type='variables_get'>
                   <field name='VAR'>list</field>
                 </block>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_split',
                    blockxml: `<block type='lists_split'>
               <value name='DELIM'>
                 <shadow type='text'>
                   <field name='TEXT'>,</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'lists_sort',
                    blockxml: `<block type='lists_sort'></block>`
                }
            ]
        },
        {
            kind: 'CATEGORY',
            name: '%{BKY_TOOLBOX_COLOR}',
            colour: '20',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'colour_picker',
                    blockxml: `<block type='colour_picker'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'colour_random',
                    blockxml: `<block type='colour_random'></block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'colour_rgb',
                    blockxml: `<block type='colour_rgb'>
               <value name='RED'>
                 <shadow type='math_number'>
                   <field name='NUM'>100</field>
                 </shadow>
               </value>
               <value name='GREEN'>
                 <shadow type='math_number'>
                   <field name='NUM'>50</field>
                 </shadow>
               </value>
               <value name='BLUE'>
                 <shadow type='math_number'>
                   <field name='NUM'>0</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'colour_blend',
                    blockxml: `<block type='colour_blend'>
               <value name='COLOUR1'>
                 <shadow type='colour_picker'>
                   <field name='COLOUR'>#ff0000</field>
                 </shadow>
               </value>
             <value name='COLOUR2'>
               <shadow type='colour_picker'>
                 <field name='COLOUR'>#3333ff</field>
               </shadow>
             </value>
             <value name='RATIO'>
               <shadow type='math_number'>
                 <field name='NUM'>0.5</field>
               </shadow>
             </value>
           </block>`
                }
            ]
        },
        {
            kind: 'SEP'
        },
        {
            kind: 'CATEGORY',
            custom: 'VARIABLE',
            colour: '330',
            name: '%{BKY_TOOLBOX_VARIABLES}'
        },
        {
            kind: 'CATEGORY',
            custom: 'PROCEDURE',
            colour: '290',
            name: '%{BKY_TOOLBOX_FUNCTIONS}'
        },
    ]
};


/***/ }),

/***/ "./lib/toolbox_turtle.js":
/*!*******************************!*\
  !*** ./lib/toolbox_turtle.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TOOLBOX_TURTLE: () => (/* binding */ TOOLBOX_TURTLE)
/* harmony export */ });
const TOOLBOX_TURTLE = {
    kind: 'categoryToolbox',
    contents: [
        {
            kind: 'CATEGORY',
            name: '%{BKY_TOOLBOX_TURTLE}',
            colour: '5',
            contents: [
                {
                    kind: 'BLOCK',
                    type: 'turtle_init',
                    blockxml: `<block type='turtle_init'>
               <value name='XSIZE'>
                 <shadow type='math_number'>
                   <field name='NUM'>600</field>
                 </shadow>
               </value>
               <value name='YSIZE'>
                 <shadow type='math_number'>
                   <field name='NUM'>600</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_speed',
                    blockxml: `<block type='turtle_speed'>
               <value name='VAL'>
                 <shadow type='math_number'>
                   <field name='NUM'>2</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_line_width',
                    blockxml: `<block type='turtle_line_width'>
               <value name='VAL'>
                 <shadow type='math_number'>
                   <field name='NUM'>2</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_line_color',
                    blockxml: `<block type='turtle_line_color'>
               <value name='VAL'>
                 <shadow type='colour_picker'>
                   <field name='COLOUR'>#000000</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_line_hsv',
                    blockxml: `<block type='turtle_line_hsv'>
               <value name='H'>
                 <shadow type='math_number'>
                   <field name='NUM'>0</field>
                 </shadow>
               </value>
               <value name='S'>
                 <shadow type='math_number'>
                   <field name='NUM'>0.45</field>
                 </shadow>
               </value>
               <value name='V'>
                 <shadow type='math_number'>
                   <field name='NUM'>0.65</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_pen_down',
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_pen_up',
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_forward',
                    blockxml: `<block type='turtle_forward'>
               <value name='VAL'>
                 <shadow type='math_number'>
                   <field name='NUM'>100</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_turn_right',
                    blockxml: `<block type='turtle_turn_right'>
               <value name='VAL'>
                 <shadow type='math_number'>
                   <field name='NUM'>90</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_turn_left',
                    blockxml: `<block type='turtle_turn_left'>
               <value name='VAL'>
                 <shadow type='math_number'>
                   <field name='NUM'>90</field>
                 </shadow>
               </value>
             </block>`
                },
                {
                    kind: 'BLOCK',
                    type: 'turtle_move',
                    blockxml: `<block type='turtle_move'>
               <value name='XPOS'>
                 <shadow type='math_number'>
                   <field name='NUM'>300</field>
                 </shadow>
               </value>
               <value name='YPOS'>
                 <shadow type='math_number'>
                   <field name='NUM'>300</field>
                 </shadow>
               </value>
             </block>`
                },
            ]
        }
    ]
};


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ToolboxUtils: () => (/* binding */ ToolboxUtils)
/* harmony export */ });
//
class ToolboxUtils {
    constructor() { }
    add(a, b, num) {
        //
        if (a.kind !== b.kind)
            undefined;
        const c = { kind: a.kind, contents: new Array };
        const a_len = a.contents.length;
        const b_len = b.contents.length;
        for (let i = 0; i < a_len; i++) {
            c.contents[i] = a.contents[i];
        }
        // separator
        for (let i = 0; i < num; i++) {
            c.contents[a_len + i] = { kind: 'SEP' };
        }
        for (let i = 0; i < b_len; i++) {
            c.contents[a_len + num + i] = b.contents[i];
        }
        return c;
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.b2dcc64b07f6a94c8ea6.js.map