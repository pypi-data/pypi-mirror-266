"use strict";(self.webpackChunk_atoti_jupyterlab_extension=self.webpackChunk_atoti_jupyterlab_extension||[]).push([[9647],{29647:(r,o,e)=>{if(e.d(o,{DP:()=>g,NP:()=>u}),4871==e.j)var n=e(63612);var t=e(77593),a=e(63259),i=e(93345),l=e(38655);if(4871==e.j)var c=e(88423);if(4871==e.j)var s=e(55789);const d=(0,i.createContext)(null),u=r=>{const o=(0,i.useMemo)((()=>(0,s.D)(r.value)),[r.value]),e=(0,c.D)(o),u=(0,i.useMemo)((()=>({accentColor:o.primaryColor,successColor:o.successColor,warningColor:o.warningColor,errorColor:o.errorColor,whiteColor:o.backgroundColor,lightGrayColor:o.grayScale[5],darkGrayColor:o.grayScale[7]})),[o]);return(0,n.Y)(d.Provider,{value:o,children:(0,n.Y)(a.ConfigProvider,{theme:e,children:(0,n.Y)(l._IconThemeContext.Provider,{value:u,children:(0,n.Y)(a.App,{className:r.className,css:t.css`
              box-sizing: border-box;
              font-size: ${e.token?.fontSizeSM}px;
              line-height: ${e.token?.lineHeight};
              font-family: ${e.token?.fontFamily};
              color: ${e.token?.colorText};
              background-color: ${e.token?.colorBgBase};
              color-scheme: ${o.isDark?"dark":"light"};

              *,
              *:before,
              *:after {
                box-sizing: inherit;
              }

              .aui-invisible-scrollbars {
                scrollbar-width: none;
              }
              .aui-invisible-scrollbars::-webkit-scrollbar {
                display: none;
              }

              .ant-picker-dropdown {
                padding: 0;
              }
              .ant-picker-range-arrow {
                ::before,
                ::after {
                  display: none;
                }
              }

              .ant-modal-footer {
                padding-inline: ${e.components?.Modal?.paddingLG}px!important;
              }

              .ant-popconfirm-buttons {
                padding-top: ${e.components?.Popconfirm?.paddingXXS}px!important;
              }

              .ant-popover {
                .ant-popover-title {
                  border-bottom: 0px;
                }

                .ant-popover-inner-content {
                  padding: 8px 12px 8px 12px;
                }
              }

              button,
              input {
                font-family: inherit;
                line-height: inherit;
                font-size: inherit;
              }

              input[type="checkbox"] {
                margin: 0;
              }

              fieldset {
                border: none;
              }

              g.pointtext {
                display: none;
              }

              /*
           * TODO Remove when upgrading Ant Design.
           * This is an Ant Design bug fixed in https://github.com/ant-design/ant-design/commit/467741f5.
           */
              .ant-dropdown-menu-sub {
                margin: 0;
              }
            `,children:r.children})})})})};function g(){const r=(0,i.useContext)(d);if(!r)throw new Error("Missing theme. Remember to add <ThemeProvider /> at the top of your application.");return r}d.Consumer},17688:(r,o,e)=>{if(e.d(o,{O:()=>l}),4871==e.j)var n=e(60589);if(4871==e.j)var t=e(91453);if(4871==e.j)var a=e(99262);const i=4871==e.j?["transparent",void 0,null]:null,l=function(r,o,e){if(i.includes(r)&&o)return(0,t.J)((0,n.p)(o),e);if(i.includes(o)&&r)return(0,t.J)((0,n.p)(r),e);if(r&&o){const t=(0,n.p)(r),i=(0,n.p)(o);return(0,a.e)(function(r,...o){return o[0].map(((e,n)=>r(...o.map((r=>r[n])))))}(((r,o)=>Math.ceil((1-e)*r+e*o)),t,i))}throw new Error("Invalid arguments to addColorLayer")}},18136:(r,o,e)=>{e.d(o,{e:()=>i});var n=e(60589),t=e(91453);const a=/\d+(\.\d*)?|\.\d+/g,i=function({color:r,opacity:o,shadeFactor:e=0,isShading:i,isInverting:l}){const c=(0,n.p)(r),s=r.startsWith("rgba")?(r=>{const o=r.match(a);if(!o)throw new SyntaxError("Invalid rgba parameter");return Number.parseFloat(o.slice(3).join(""))})(r):1;return(0,t.J)(c.map((r=>{const o=l?(r=>255-r)(r):r;return n=i?o*(1-e):o+(255-o)*e,Math.max(0,Math.min(255,n));var n})),(d=s*o,Math.max(0,Math.min(1,d))));var d}},85156:(r,o,e)=>{if(e.d(o,{w:()=>t}),4871==e.j)var n=e(17688);const t=(r,o)=>{const e=e=>(0,n.O)(r,o,e);return[e(0),e(.02),e(.04),e(.06),e(.09),e(.15),e(.25),e(.45),e(.55),e(.65),e(.75),e(.85),e(.95),e(1)]}},88423:(r,o,e)=>{e.d(o,{D:()=>t});var n=e(63259);function t(r){return{token:{lineHeight:1.66667,fontSizeSM:12,fontFamily:"-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif, Apple Color Emoji, Segoe UI Emoji, Segoe UI Symbol, Noto Color Emoji",borderRadius:2,controlOutlineWidth:0,colorPrimary:r.primaryColor,colorSuccess:r.successColor,colorWarning:r.warningColor,colorText:r.textColor,colorTextPlaceholder:r.placeholderColor,colorTextDisabled:r.disabledTextColor,colorBgBase:r.backgroundColor,colorPrimaryBg:r.selectedMenuItemBackground,colorBgContainerDisabled:r.disabledBackground,colorBorder:r.cellBorderColor,colorBorderSecondary:r.cellBorderColor,colorLink:r.textColor,colorLinkHover:r.primaryColor},components:{Menu:{radiusItem:0,radiusSubMenuItem:0,lineWidth:.5,margin:12,controlHeightLG:32,colorActiveBarBorderSize:0,colorActiveBarWidth:3,colorItemTextSelected:r.primaryColor,colorSubItemBg:r.menuInlineSubmenuBg},Tooltip:{paddingXS:8,paddingSM:12},Checkbox:{paddingXS:8},Modal:{wireframe:!0,paddingXS:8,marginXS:8,padding:11,paddingLG:16},Popover:{wireframe:!0,padding:12,paddingSM:12},Popconfirm:{marginXS:8,paddingXXS:4},Card:{padding:8.5,paddingLG:12,fontWeightStrong:500},Dropdown:{marginXS:8,controlPaddingHorizontal:8},Tabs:{colorText:r.grayScale[8],colorFillAlter:r.grayScale[3]}},algorithm:[n.theme.compactAlgorithm,...r.isDark?[n.theme.darkAlgorithm]:[],(r,o=n.theme.defaultAlgorithm(r))=>({...o,colorInfo:r.colorPrimary,colorBgContainer:r.colorBgBase,colorBgElevated:r.colorBgBase,colorBgLayout:r.colorBgBase})]}}},55789:(r,o,e)=>{e.d(o,{D:()=>c});var n=e(15320);if(4871==e.j)var t=e(85156);if(4871==e.j)var a=e(67315);if(4871==e.j)var i=e(31927);if(4871==e.j)var l=e(46994);function c(r){const o=!r.isDark,e=r.white??o?"#FFFFFF":"#000000",c=r.black??o?"#000000":"#FFFFFF",s=r.backgroundColor??e,d=(0,t.w)(s,c),u=(0,l.k)([(0,i.z)(r.primaryColor)[0],"100","50"]),g=r.successColor??"#52C41A",p=r.errorColor??"#F5222D",m=(0,n.cM)(r.primaryColor,{theme:o?"default":"dark",backgroundColor:s});return{activeMenuItemBackgroundColor:d[4],activeTabBackgroundColor:d[0],alternateCellBackgroundColor:(0,a.j)(d[2],.65),alternateBackgroundColor:d[1],backgroundColor:s,black:c,cellBackgroundDuringNegativeTransition:(0,a.j)(p,.7),cellBackgroundDuringPositiveTransition:(0,a.j)(g,.7),cellBorderColor:d[5],headerActiveColor:r.primaryColor,disabledBackground:o?"#F5F5F5":s,disabledTextColor:o?(0,a.j)(c,.35):(0,a.j)(c,.25),dropHintBorderColor:(0,a.j)(u,.2),dropHintColor:(0,a.j)(u,.15),errorColor:p,grayScale:d,hoverColor:m[5],inactiveTabBackgroundColor:d[2],menuInlineSubmenuBg:"transparent",placeholderColor:d[6],primaryScale:m,selectedMenuItemBackground:m[0],selectionOverlayColor:(0,a.j)(u,.1),selectionMarkDarkColor:"#646464",selectionMarkLightColor:"#FFFFFF",selectionColor:m[0],shadowColor:"#000C11",successColor:g,textColor:o?d[11]:(0,a.j)(c,.65),warningColor:"#FAAD14",white:e,...r}}},60589:(r,o,e)=>{function n(r,o,e){const n=(e+1)%1;return n<1/6?r+6*(o-r)*n:n<.5?o:n<2/3?r+(o-r)*(2/3-n)*6:r}e.d(o,{p:()=>i});const t=/\d+/g,a=/\d+(\.\d*)?|\.\d+/g,i=function(r){const o=r.toLowerCase();if(o.startsWith("#"))return function(r){if(6!==r.length&&3!==r.length)throw new Error(`Hex color (${r}) is not a valid 3 or 6 character string`);const o=6===r.length?r:r.charAt(0).repeat(2)+r.charAt(1).repeat(2)+r.charAt(2).repeat(2);return[Number.parseInt(o.slice(0,2),16),Number.parseInt(o.slice(2,4),16),Number.parseInt(o.slice(4,6),16)]}(r.slice(1));if(o.startsWith("rgb"))return(r=>{const o=r.match(t);if(!o)throw new SyntaxError("Invalid rgb parameter");const e=o.slice(0,3).map((r=>Number(r)));return[e[0],e[1],e[2]]})(r);if(o.startsWith("hsl"))return(r=>{const o=r.match(a);if(!o)throw new SyntaxError("Invalid hsl parameter");const e=o.slice(0,3).map((r=>Number(r)));return function(r,o,e){let t,a,i;const l=r/360,c=o/100,s=e/100;if(0===c)i=s,a=s,t=s;else{const r=s<.5?s*(1+c):s+c-s*c,o=2*s-r;t=n(o,r,l+1/3),a=n(o,r,l),i=n(o,r,l-1/3)}return t=Math.round(255*t),a=Math.round(255*a),i=Math.round(255*i),[t,a,i]}(e[0],e[1],e[2])})(r);throw new Error("Unsupported color syntax. Supported syntaxes are rgb, hsl and hex.")}},67315:(r,o,e)=>{e.d(o,{j:()=>t});var n=e(18136);function t(r,o=1){return(0,n.e)({color:r,opacity:o})}},6826:(r,o,e)=>{function n(r,o,e){const n=r/255,t=o/255,a=e/255,i=Math.max(n,t,a),l=Math.min(n,t,a);let c=0,s=0,d=(i+l)/2;if(i!==l){const r=i-l;switch(s=d>.5?r/(2-i-l):r/(i+l),i){case n:c=(t-a)/r+(t<a?6:0);break;case t:c=(a-n)/r+2;break;case a:c=(n-t)/r+4}c/=6}return c=Math.round(360*c),s=Math.round(100*s),d=Math.round(100*d),[c,s,d]}e.d(o,{K:()=>n})},31927:(r,o,e)=>{if(e.d(o,{z:()=>a}),4871==e.j)var n=e(60589);if(4871==e.j)var t=e(6826);function a(r){return(0,t.K)(...(0,n.p)(r))}},46994:(r,o,e)=>{function n(r){return`hsl(${r[0]}, ${r[1]}%, ${r[2]}%)`}e.d(o,{k:()=>n})},91453:(r,o,e)=>{e.d(o,{J:()=>n});const n=function(r,o){return`rgba(${r.join(", ")}, ${o})`}},99262:(r,o,e)=>{e.d(o,{e:()=>n});const n=function(r){return`rgb(${r.join(", ")})`}}}]);