<template>
  <div class="container">
    <!-- 标题 -->
    <div class="section-title">申万行业持仓</div>
    <!-- 单列 -->
    <div class="half-container">
      <div class="index-cell" v-for="(item, i) in swIndustryHoldings" v-if="i % 2 === 0" :key="item.index" >
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.sw1_name}}</p>
        <p class="index-value">{{item.holding_money}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.rate)/100)">{{item.rate}}</p>
      </div>
    </div>
    <!-- 双列 -->
    <div class="half-container">
    <div class="index-cell" v-for="(item, i) in swIndustryHoldings" v-if="i % 2 === 1" :key="item.index" >
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.sw1_name}}</p>
        <p class="index-value">{{item.holding_money}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.rate)/100)">{{item.rate}}</p>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'IndexHoldingComponent',
  props: ['swIndustryHoldings'],
  methods: {
    swIndustryIndexColor (item, index) {
      var bgClass = 'index-name-color'
      if ([0, 1, 2, 3].indexOf(index) > -1) {
        return bgClass + 1
      } else if ([4, 5, 6, 7].indexOf(index) > -1) {
        return bgClass + 2
      } else if ([8, 9, 10, 11].indexOf(index) > -1) {
        return bgClass + 3
      } else if ([12, 13, 14, 15].indexOf(index) > -1) {
        return bgClass + 4
      } else if ([16, 17, 18, 19].indexOf(index) > -1) {
        return bgClass + 5
      } else if ([20, 21, 22, 23].indexOf(index) > -1) {
        return bgClass + 6
      } else if ([24, 25, 26, 27].indexOf(index) > -1) {
        return bgClass + 7
      } else {
        return bgClass + 0
      }
    },
    evalRankBackground (percentile) {
      if (percentile === 0.0) {
        return 'background-color:#333'
      }
      var style = ''
      if (percentile <= 0.05) {
        style = 'background: linear-gradient(90deg, #0fae9d ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
        return style
      } else if (percentile > 0.05 && percentile <= 0.1) {
        style = 'background: linear-gradient(90deg, #e5a43a ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
        return style
      } else if (percentile > 0.1) {
        if (1 - percentile < 0.1) {
          var tailRate = 1 - percentile
          style = 'background: linear-gradient(90deg, #fe5a4b ' + percentile * 100 + '%,#333333 ' + (percentile + tailRate) * 100 + '%);'
        } else {
          style = 'background: linear-gradient(90deg, #fe5a4b ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
        }
        return style
      } else {
        return 'background-color: #333'
      }
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

.container {
  display: flex;
  flex-wrap:wrap;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.section-title {
  display: flex;
  flex-wrap:wrap;
  justify-content: center;
  font-size: 0.33rem;
  width: 100%;
  height: 0.5rem;
  margin: 0px;
  padding: 0px;
  color:#FFFFFF;
  background-color: #333333;
}

.half-contianer {
  display: flex;
  flex-wrap:wrap;
  align-items: center;
  justify-content: center;
  width: 50%;
  height: 100%;
}

.index-cell {
  display: flex;
  width: 5rem;
  justify-content:flex-start;
  /* justify-content:flex-start; */
  align-items: center;
  margin: 0px;
  padding: 0px;
  background-color: #000000;
}

.index-name {
    /* 解决纯数字时偏上的问题 */
  display: flex;
  justify-content:center;
  align-items: center;
  margin: 1px;
  padding: 1px;
  width: 1.7rem;
  height: 0.5rem;
  font-size: 0.33rem;
  color:#FFFFFF;
  background-color: #333333;
}

.index-value {
    /* 解决纯数字时偏上的问题 */
  display: flex;
  justify-content:flex-end;
  align-items: center;
  margin: 1px;
  padding: 1px;
  width: 1.65rem;
  height: 0.5rem;
  font-size: 0.33rem;
  /* text-align: center; */
  color:#FFFFFF;
  background-color: #333333;
}

/* 指数名称背景色 */
.index-name-color0 {
  color:#FFFFFF;
  background-color: #333333;
}
.index-name-color1 {
  color:#333333;
  background-color: #50C2F9;
}
.index-name-color2 {
  color:#333333;
  background-color: #BBEDA8;
}
.index-name-color3 {
  color:#333333;
  background-color: #FFC751;
}
.index-name-color4 {
  color:#333333;
  background-color: #FF7C9E;
}
.index-name-color5 {
  color:#333333;
  background-color: #FF8361;
}
.index-name-color6 {
  color:#333333;
  background-color: #DBB6AC;
}
.index-name-color7 {
  color:#333333;
  background-color: #DCDCDC;
}
.index-name-color8 {
  color:#333333;
  background-color: #F0DC5A;
}
</style>
