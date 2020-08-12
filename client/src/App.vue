<template>
  <div id="app">
    <div style="display:flex; justify-content:center; color:#FFF; margin:4px; width:100%;font-size: 0.33rem;">{{datetime}}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;距下次更新约 {{myCountdown}} 秒</div>
    <!-- 数据区 -->
    <IndexValueComponent :swIndustryValues="swIndustryValues" :swStyleValues="swStyleValues"/>
    <!-- <div style="background-color:#000; width:10rem;" v-for="item in swIndustryValues" :key="item.index">
      <div style="color:#FFF; width:10rem;">{{item.name}}</div>
    </div> -->
  </div>
</template>

<script>

import IndexValueComponent from './components/IndexValueComponent'

import axios from 'axios'
import Vue from 'vue'

Vue.prototype.$axios = axios
Vue.config.productionTip = false

// 根据不同环境，动态切换 API 域名
var serverIp = process.env.API_ROOT

export default {
  name: 'App',
  components: {
    IndexValueComponent
  },
  data () {
    return {
      datetime: '',
      refreshInterval: 90,
      myCountdown: 0,
      swIndustryValues: [],
      swStyleValues: [],
      swIndustryEvals: []
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
    getSWIndexValues () {
      var that = this
      axios.get(serverIp + 'shenwan/api/index_value').then(function (response) {
        // 申万行业指数
        that.swIndustryValues = response.data.data.sw_indexs
        // 申万风格指数
        that.swStyleValues = response.data.data.sw_styles

        that.myCountdown = that.refreshInterval
      })
    }
  },
  created: function () {
    // var that = this
    // document.onkeyup = function (e) {
    //   // console.log(e.keyCode)
    //   var val = that.active
    //   // 事件对象兼容
    //   let e1 = e || event || window.event
    //   // 键盘按键判断:左箭头-37;上箭头-38；右箭头-39;下箭头-40
    //   if (e1 && e1.keyCode === 37) {
    //     // console.log('左')
    //     if (val > 0) {
    //       val -= 1
    //     } else {
    //       val = 1
    //     }
    //     that.toggle(val)
    //   } else if (e1 && e1.keyCode === 38) {
    //     // console.log('上')
    //   } else if (e1 && e1.keyCode === 39) {
    //     // console.log('右')
    //     if (val < 1) {
    //       val += 1
    //     } else {
    //       val = 0
    //     }
    //     that.toggle(val)
    //   } else if (e1 && e1.keyCode === 40) {
    //     // console.log('下')
    //   } else if (e1 && e1.keyCode === 32) {
    //     // console.log('空格')
    //   }
    // }
    this.myCountdown = this.refreshInterval
    this.updateTime()
    setInterval(this.updateTime, 1 * 1000)
    // 获取指数点位
    this.getSWIndexValues()
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

</style>
