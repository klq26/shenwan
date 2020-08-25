<template>
  <div class="container">
    <!-- 历史大顶大底 -->
    <div class="section-title" @click="showDistance = !showDistance">历史数据</div>
    <!-- 标题 -->
    <div class="sw-industry-container" v-show="showDistance" @click="showDistance = !showDistance">
      <div class="index-cell">
        <p class="index-name history-title-width">位置</p>
        <p class="index-name date-width">日期</p>
        <p class="index-name">PE</p>
        <p class="index-name">PE 距离</p>
        <p class="index-name">PB</p>
        <p class="index-name">PB 距离</p>
      </div>
    </div>
    <!-- 数据 -->
    <div class="sw-industry-container" v-show="showDistance">
      <!-- 历史大顶 -->
      <div class="index-cell" v-for="item in swUltimates.to_tops" :key="item.index">
        <p class="index-name top-bg-color history-title-width">顶部</p>
        <p class="index-name top-bg-color date-width">{{item.date}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pe).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pe_distance)">{{parseFloat(item.pe_distance).toFixed(2)+'%'}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pb).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pb_distance)">{{parseFloat(item.pb_distance).toFixed(2)+'%'}}</p>
      </div>
      <!-- 历史大底 -->
      <div class="index-cell" v-for="item in swUltimates.to_bottoms" :key="item.index">
        <p class="index-name bottom-bg-color history-title-width">底部</p>
        <p class="index-name bottom-bg-color date-width">{{item.date}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pe).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pe_distance)">{{parseFloat(item.pe_distance).toFixed(2)+'%'}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pb).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pb_distance)">{{parseFloat(item.pb_distance).toFixed(2)+'%'}}</p>
      </div>
      <!-- 近期以来 -->
      <div class="index-cell" v-for="(item, i) in swUltimates.to_recents" :key="item.index">
        <p class="index-name recent-bg-color history-title-width">{{recentTtitles[i]}}</p>
        <p class="index-name recent-bg-color date-width">{{item.date}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pe).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pe_distance)">{{parseFloat(item.pe_distance).toFixed(2)+'%'}}</p>
        <p class="index-name index-value-right">{{parseFloat(item.pb).toFixed(2)}}</p>
        <p class="index-name index-value-right" :class="colorWithValue(item.pb_distance)">{{parseFloat(item.pb_distance).toFixed(2)+'%'}}</p>
      </div>
    </div>
    <!-- 估值 -->
    <div class="section-title">申万行业估值</div>
    <!-- 标题 -->
    <div class="sw-industry-container">
      <div class="index-cell">
        <p class="index-name">名称</p>
        <p class="index-name">代码</p>
        <p class="index-value index-title-center">股个数</p>
        <!-- 变化列 1 -->
        <p class="index-value index-title-center" v-if="showType==0">PE&#60;0</p>
        <p class="index-value index-title-center" v-else-if="showType==1">PE_3Y</p>
        <p class="index-value index-title-center" v-else>PB_3Y</p>
        <!-- 变化列 2 -->
        <p class="index-value index-title-center" v-if="showType==0">PE&#62;125</p>
        <p class="index-value index-title-center" v-else-if="showType==1">PE_5Y</p>
        <p class="index-value index-title-center" v-else>PB_5Y</p>
        <!-- 变化列 3 -->
        <p class="index-value index-title-center" v-if="showType==0">PE</p>
        <p class="index-value index-title-center" v-else-if="showType==1">PE_10Y</p>
        <p class="index-value index-title-center" v-else>PB_10Y</p>
        <!-- 变化列 4 -->
        <p class="index-value index-title-center" v-if="showType==0">PB</p>
        <p class="index-value index-title-center" v-else-if="showType==1">PE_ALL</p>
        <p class="index-value index-title-center" v-else>PB_ALL</p>
      </div>
    </div>
    <!-- 数据 -->
    <div class="sw-industry-container" @click="changeShowType()">
      <div class="index-cell" v-for="(item, i) in swIndustryEvals" :key="item.index" >
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.sw1_name}}</p>
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.sw1_code}}</p>
        <p class="index-value" :style="evalRankBackground(item.total_count / allMarket.total_count == 1 ? 0 : item.total_count / allMarket.total_count)">{{item.total_count}}</p>
        <!-- 变化列 1 -->
        <p class="index-value" v-if="showType==0" :style="evalRankBackground(item.pe_negative_count / allMarket.pe_negative_count == 1 ? 0 : item.pe_negative_count / allMarket.pe_negative_count)">{{item.pe_negative_count}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pe_percentile_3y)/100)" v-else-if="showType==1">{{parseFloat(item.pe_percentile_3y).toFixed(1)+'%'}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pb_percentile_3y)/100)" v-else>{{parseFloat(item.pb_percentile_3y).toFixed(1)+'%'}}</p>
        <!-- 变化列 2 -->
        <p class="index-value" v-if="showType==0" :style="evalRankBackground(item.pe_over_125_count / allMarket.pe_over_125_count == 1 ? 0 : item.pe_over_125_count / allMarket.pe_over_125_count)">{{item.pe_over_125_count}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pe_percentile_5y)/100)" v-else-if="showType==1">{{parseFloat(item.pe_percentile_5y).toFixed(1)+'%'}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pb_percentile_5y)/100)" v-else>{{parseFloat(item.pb_percentile_5y).toFixed(1)+'%'}}</p>
        <!-- 变化列 3 -->
        <p class="index-value" v-if="showType==0">{{item.pe.toFixed(2)}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pe_percentile_10y)/100)" v-else-if="showType==1">{{parseFloat(item.pe_percentile_10y).toFixed(1)+'%'}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pb_percentile_10y)/100)" v-else>{{parseFloat(item.pb_percentile_10y).toFixed(1)+'%'}}</p>
        <!-- 变化列 4 -->
        <p class="index-value" v-if="showType==0">{{item.pb.toFixed(2)}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pe_percentile)/100)" v-else-if="showType==1">{{parseFloat(item.pe_percentile).toFixed(1)+'%'}}</p>
        <p class="index-value" :style="evalRankBackground(parseFloat(item.pb_percentile)/100)" v-else>{{parseFloat(item.pb_percentile).toFixed(1)+'%'}}</p>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  name: 'IndexValueComponent',
  props: ['swIndustryEvals', 'swUltimates'],
  methods: {
    colorWithValue (value) {
      var number = parseFloat(value)
      if (number > 0) {
        return 'top-bg-color'
      } else if (number === 0) {
        return 'normal-bg-color'
      } else {
        return 'bottom-bg-color'
      }
    },
    evalRankBackground (percentile) {
      if (percentile === 0.0) {
        return 'background-color:#333'
      }
      var style = ''
      if (percentile <= 0.4) {
        style = 'background: linear-gradient(90deg, #0fae9d ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
        return style
      } else if (percentile > 0.4 && percentile <= 0.8) {
        style = 'background: linear-gradient(90deg, #e5a43a ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
        return style
      } else if (percentile > 0.8) {
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
    },
    swIndustryIndexColor (item, index) {
      var bgClass = 'index-name-color'
      if ([0].indexOf(index) > -1) {
        return bgClass + 0
      } else if ([1, 2, 3, 4].indexOf(index) > -1) {
        return bgClass + 1
      } else if ([5, 6, 7, 8].indexOf(index) > -1) {
        return bgClass + 2
      } else if ([9, 10, 11, 12].indexOf(index) > -1) {
        return bgClass + 3
      } else if ([13, 14, 15, 16].indexOf(index) > -1) {
        return bgClass + 4
      } else if ([17, 18, 19, 20].indexOf(index) > -1) {
        return bgClass + 5
      } else if ([21, 22, 23, 24].indexOf(index) > -1) {
        return bgClass + 6
      } else if ([25, 26, 27, 28].indexOf(index) > -1) {
        return bgClass + 7
      } else {
        return bgClass + 0
      }
    },
    changeShowType () {
      if (this.showType < 2) {
        this.showType += 1
      } else {
        this.showType = 0
      }
    //   console.log(this.showType)
    }
  },
  created: function () {
    this.showType = 0
  },
  watch: {
    swIndustryValues: {
      handler (newValue, oldValue) {
        if (newValue !== 'undefined') {
          // this.allMarket = this.mySWIndustryEvals[0]
          // console.log(this.allMarket)
        }
      },
      immediate: true,
      deep: true
    }
  },
  data () {
    return {
      showType: 0,
      showDistance: true,
      recentTtitles: ['一年','半年','季度'],
      mySWIndustryEvals: this.swIndustryEvals,
      mySWUltimates: this.swUltimates,
      allMarket: {}
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

.sw-industry-container {
  display: flex;
  flex-wrap:wrap;
  align-items: left;
  justify-content: left;
  width: 100%;
  height: 100%;
}

.index-cell {
  display: flex;
  width: 10rem;
  justify-content:flex-start;
  /* justify-content:flex-start; */
  align-items: center;
  margin: 0px;
  padding: 0px;
  width: 100%;
  background-color: #000000;
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
  width: 1.32rem;
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

.recent-bg-color {
  background-color: #50C2F9;
}
.top-bg-color {
  background-color: #EE2200;
}
.bottom-bg-color {
  background-color: #00CC22;
}

.history-title-width {
  width:0.8rem;
}

.date-width {
  width:2rem;
}

.index-value-right {
  justify-content: flex-end;
}

.index-title-center {
  justify-content: center;
}

</style>
