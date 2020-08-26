<template>
  <div id="app">
    <ul>
      <li v-for="(tab, index) in tabs" @click="toggle(index)" :class="{active: active == index}" :key=index>
        {{tab.type}}
      </li>
    </ul>
    <div style="display:flex; justify-content:center; color:#FFF; margin:4px; width:100%;font-size: 0.33rem;">{{datetime}}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;距下次更新约 {{myCountdown}} 秒</div>
    <!-- 数据区 -->
    <IndexValueComponent :swIndustryValues="swIndustryValues" :swStyleValues="swStyleValues" v-show="active == 0"/>
    <!-- 估值区 -->
    <IndexEvalComponent :swIndustryEvals="swIndustryEvals" :swUltimates="swUltimates" v-show="active == 1"/>
    <!-- 持仓区 -->
    <IndexHoldingComponent :swIndustryHoldings="swIndustryHoldings" v-show="active == 2"/>
  </div>
</template>

<script>

import IndexValueComponent from './components/IndexValueComponent'
import IndexEvalComponent from './components/IndexEvalComponent'
import IndexHoldingComponent from './components/IndexHoldingComponent'

import axios from 'axios'
import Vue from 'vue'

Vue.prototype.$axios = axios
Vue.config.productionTip = false

// 根据不同环境，动态切换 API 域名
var serverIp = process.env.API_ROOT

export default {
  name: 'App',
  components: {
    IndexValueComponent,
    IndexEvalComponent,
    IndexHoldingComponent
  },
  data () {
    return {
      datetime: '',
      refreshInterval: 90,
      myCountdown: 0,
      active: 0,
      tabs: [
        {
          type: '申万指数'
        },
        {
          type: '申万估值'
        },
        {
          type: '申万持仓'
        }
      ],
      swIndustryValues: [],
      swStyleValues: [],
      swIndustryEvals: [],
      swUltimates: [],
      swIndustryHoldings: []
    }
  },
  methods: {
    updateTime () {
      var date = new Date()
      var year = date.getFullYear()
      var month = this.prefixInteger(date.getMonth() + 1, 2)
      var day = this.prefixInteger(date.getDate(), 2)
      var hh = this.prefixInteger(date.getHours(), 2)
      var mi = this.prefixInteger(date.getMinutes(), 2)
      var ss = this.prefixInteger(date.getSeconds(), 2)
      this.datetime = year + '-' + month + '-' + day + ' ' + hh + ':' + mi + ':' + ss + ' '
      if (this.myCountdown > 0) {
        this.myCountdown = this.myCountdown - 1
      }
    },
    // 时间前置补 0
    prefixInteger (num, length) {
      return (Array(length).join('0') + num).slice(-length)
    },
    toggle (i) {
      this.active = i
    },
    getSWIndexValues () {
      var that = this
      axios.get(serverIp + 'shenwan/api/index_value').then(function (response) {
        // 申万行业指数
        that.swIndustryValues = response.data.data.sw_indexs
        // 申万风格指数
        that.swStyleValues = response.data.data.sw_styles

        that.myCountdown = that.refreshInterval
      })
    },
    getSWIndexEvals () {
      var that = this
      axios.get(serverIp + 'shenwan/api/index_eval').then(function (response) {
        // 申万行业估值数据
        that.swIndustryEvals = response.data.data.eval
        // 申万全市场历史大顶大底数据
        that.swUltimates = response.data.data.ultimate
      })
    },
    getSWIndexHoldings () {
      var that = this
      axios.get(serverIp + 'shenwan/api/index_holding').then(function (response) {
        // 申万行业持仓数据
        that.swIndustryHoldings = response.data.data
      })
    }
  },
  created: function () {
    var that = this
    document.onkeyup = function (e) {
      // console.log(e.keyCode)
      var val = that.active
      // 事件对象兼容
      let e1 = e || event || window.event
      // 键盘按键判断:左箭头-37;上箭头-38；右箭头-39;下箭头-40
      if (e1 && e1.keyCode === 37) {
        // console.log('左')
        if (val > 0) {
          val -= 1
        } else {
          val = 2
        }
        that.toggle(val)
      } else if (e1 && e1.keyCode === 38) {
        // console.log('上')
      } else if (e1 && e1.keyCode === 39) {
        // console.log('右')
        if (val < 2) {
          val += 1
        } else {
          val = 0
        }
        that.toggle(val)
      } else if (e1 && e1.keyCode === 40) {
        // console.log('下')
      } else if (e1 && e1.keyCode === 32) {
        // console.log('空格')
      }
    }
    this.myCountdown = this.refreshInterval
    this.updateTime()
    setInterval(this.updateTime, 1 * 1000)
    // 获取指数点位
    this.getSWIndexValues()
    // 获取指数估值
    this.getSWIndexEvals()
    // 获取指数持仓
    this.getSWIndexHoldings()
    // // 给首次估值一个 500 毫秒的延迟执行，防止后者先回来，没有更新页面
    // setTimeout(() => {
    //   that.familyEstimate()
    // }, 500)
    // 每 15 秒更新一次
    setInterval(this.getSWIndexValues, this.refreshInterval * 1000)
  }
}
</script>

<style>
#app {
  width: 10rem;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

ul{
  width:10rem;
  display:flex;
}

ul li{
  width:3.333rem;
  height:1rem;
  background: #F0F0F0;
  display: inline-flex;
  border-right:1px solid #333333;
  justify-content: center;
  align-items: center;
  cursor:pointer;
  font-size: 0.4rem;
}

ul li.active{
  background-color: rgb(51,153,254);
  font-weight: bold;
}

</style>
