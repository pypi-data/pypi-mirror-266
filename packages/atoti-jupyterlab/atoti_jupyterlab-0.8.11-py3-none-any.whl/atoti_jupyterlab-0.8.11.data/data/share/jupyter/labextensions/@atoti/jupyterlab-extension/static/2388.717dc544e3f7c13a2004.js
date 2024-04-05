"use strict";(self.webpackChunk_atoti_jupyterlab_extension=self.webpackChunk_atoti_jupyterlab_extension||[]).push([[2388],{82388:(e,t,a)=>{a.d(t,{FiltersBarDateRangePicker:()=>p});var r=a(63612),n=a(77593),s=a(63259),i=a(42579),l=a.n(i),c=a(38655),o=a(29647),d=a(64688);const g=s.DatePicker.RangePicker,p=({filter:e,onFilterChanged:t})=>{const a=(0,o.DP)(),{startDate:s,endDate:i}=e;return(0,r.Y)(d.o,{levelName:e.levelName,children:(0,r.FD)("div",{css:n.css`
          display: flex;
          align-items: center;
          border: 1px solid ${a.grayScale[5]};
          border-radius: 2px;
          height: 33px;
        `,children:[e.isExclusionFilter&&(0,r.Y)(c.IconExclude,{style:{marginLeft:3,marginRight:5}}),(0,r.Y)(g,{css:n.css`
            margin: 0 4px 0 0;
          `,value:[l()(s),l()(i)],onChange:a=>{const[r,n]=a,s={...e,startDate:r.toDate(),endDate:n.toDate()};t(s)},placement:"bottomLeft",bordered:!1,allowClear:!1})]})})}}}]);