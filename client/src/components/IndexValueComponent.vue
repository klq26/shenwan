<template>
  <div class="container"><!--  @click="showDaily = !showDaily" -->
    <!-- 标题 -->
    <div class="section-title">申万行业指数</div>
    <!-- 申万行业指数 -->
    <!-- 单列 -->
    <div class="half-container">
      <div class="index-cell" v-for="(item, i) in mySWIndustryValues" v-if="i % 2 === 0" :key="item.index" >
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.name}}</p>
        <p class="index-value" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{item.current}}</p>
        <p class="index-value" style="width: 1.3rem;" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{(((item.current / item.last_close) - 1) * 100).toFixed(2) + '%'}}</p>
        <img class="change-icon" :class="{flash : isUpdating}" :src="iconWithValue(item.change)"/>
      </div>
    </div>
    <!-- 双列 -->
    <div class="half-container">
    <div class="index-cell" v-for="(item, i) in mySWIndustryValues" v-if="i % 2 === 1" :key="item.index" >
        <p class="index-name" :class="swIndustryIndexColor(item, i)">{{item.name}}</p>
        <p class="index-value" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{item.current}}</p>
        <p class="index-value" style="width: 1.3rem;" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{(((item.current / item.last_close) - 1) * 100).toFixed(2) + '%'}}</p>
        <img class="change-icon" :class="{flash : isUpdating}" :src="iconWithValue(item.change)"/>
      </div>
    </div>
    <!-- 申万风格指数 -->
    <div class="section-title">申万风格指数</div>
    <!-- 单列 -->
    <div class="half-container">
      <div class="index-cell" v-for="(item, i) in mySWStyleValues" v-if="[0, 1, 2, 6, 7, 8, 12, 13].indexOf(i) > -1" :key="item.index">
        <p class="index-name" :class="swStyleIndexColor(item, i)">{{item.name}}</p>
        <p class="index-value" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{item.current}}</p>
        <p class="index-value" style="width: 1.3rem;" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{(((item.current / item.last_close) - 1) * 100).toFixed(2) + '%'}}</p>
        <img class="change-icon" :class="{flash : isUpdating}" :src="iconWithValue(item.change)"/>
      </div>
    </div>
    <!-- 双列 -->
    <div class="half-container">
      <div class="index-cell" v-for="(item, i) in mySWStyleValues" v-if="[3, 4, 5, 9, 10, 11, 14, 15].indexOf(i) > -1" :key="item.index">
        <p class="index-name" :class="swStyleIndexColor(item, i)">{{item.name}}</p>
        <p class="index-value" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{item.current}}</p>
        <p class="index-value" style="width: 1.3rem;" :class="[textColorWithValue((item.current / item.last_close) - 1), {flash : isUpdating}]">{{(((item.current / item.last_close) - 1) * 100).toFixed(2) + '%'}}</p>
        <img class="change-icon" :class="{flash : isUpdating}" :src="iconWithValue(item.change)"/>
      </div>
    </div>
  </div>
</template>

<script>

// 图片资源
import iconUp from '../assets/icon_up.png'
import iconEqual from '../assets/icon_equal.png'
import iconDown from '../assets/icon_down.png'

export default {
  name: 'IndexValueComponent',
  props: ['swIndustryValues', 'swStyleValues'],
  methods: {
    // 根据数值决定所使用的 icon
    iconWithValue (value) {
      var number = parseFloat(value)
      if (number > 0) {
        return iconUp
      } else if (Math.abs(number - 0.03) > 0) {
        return iconEqual
      } else {
        return iconDown
      }
    },
    // 文字颜色
    textColorWithValue (value) {
      var number = parseFloat(value)
      if (number > 0) {
        return 'rise-text-color'
      } else if (number === 0) {
        return 'normal-text-color'
      } else {
        return 'fall-text-color'
      }
    },
    // evalRankBackground (percentile) {
    //   if (percentile === 0.0) {
    //     return 'background-color:#333'
    //   }
    //   var style = ''
    //   if (percentile <= 0.4) {
    //     style = 'background: linear-gradient(90deg, #0fae9d ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
    //     return style
    //   } else if (percentile > 0.4 && percentile <= 0.8) {
    //     style = 'background: linear-gradient(90deg, #e5a43a ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
    //     return style
    //   } else if (percentile > 0.8) {
    //     if (1 - percentile < 0.1) {
    //       var tailRate = 1 - percentile
    //       style = 'background: linear-gradient(90deg, #fe5a4b ' + percentile * 100 + '%,#333333 ' + (percentile + tailRate) * 100 + '%);'
    //     } else {
    //       style = 'background: linear-gradient(90deg, #fe5a4b ' + percentile * 100 + '%,#333333 ' + (percentile + 0.1) * 100 + '%);'
    //     }
    //     return style
    //   } else {
    //     return 'background-color: #333'
    //   }
    // },
    swIndustryIndexColor (item, index) {
      var bgClass = 'index-name-color'
      if ([0, 1].indexOf(index) > -1) {
        return bgClass + 0
      } else if ([2, 3, 4, 5].indexOf(index) > -1) {
        return bgClass + 1
      } else if ([6, 7, 8, 9].indexOf(index) > -1) {
        return bgClass + 2
      } else if ([10, 11, 12, 13].indexOf(index) > -1) {
        return bgClass + 3
      } else if ([14, 15, 16, 17].indexOf(index) > -1) {
        return bgClass + 4
      } else if ([18, 19, 20, 21].indexOf(index) > -1) {
        return bgClass + 5
      } else if ([22, 23, 24, 25].indexOf(index) > -1) {
        return bgClass + 6
      } else if ([26, 27, 28, 29].indexOf(index) > -1) {
        return bgClass + 7
      } else {
        return bgClass + 0
      }
    },
    swStyleIndexColor (item, index) {
      var bgClass = 'index-name-color'
      if ([0, 1, 2].indexOf(index) > -1) {
        return bgClass + 1
      } else if ([3, 4, 5].indexOf(index) > -1) {
        return bgClass + 2
      } else if ([6, 7, 8].indexOf(index) > -1) {
        return bgClass + 3
      } else if ([9, 10, 11].indexOf(index) > -1) {
        return bgClass + 4
      } else if ([12, 13, 14].indexOf(index) > -1) {
        return bgClass + 5
      } else if ([15, 16, 17].indexOf(index) > -1) {
        return bgClass + 6
      } else {
        return bgClass + 0
      }
    }
  },
  data () {
    return {
      showEval: false,
      isUpdating: true,
      mySWIndustryValues: this.swIndustryValues,
      mySWStyleValues: this.swStyleValues,
      lastValues: {}
    }
  },
  created: function () {},
  watch: {
    swIndustryValues: {
      handler (newValue, oldValue) {
        this.mySWIndustryValues = this.swIndustryValues
        // 计算变化值
        if (typeof (oldValue) !== 'undefined') {
          for (var index in this.mySWIndustryValues) {
            var indexItem = this.mySWIndustryValues[index]
            for (var oldIndex in oldValue) {
              var oldIndexItem = oldValue[oldIndex]
              if (oldIndexItem.code === indexItem.code) {
                indexItem['change'] = indexItem.current - oldIndexItem.current
                break
              }
            }
          }
        } else {
          for (index in this.mySWIndustryValues) {
            indexItem = this.mySWIndustryValues[index]
            indexItem['change'] = 0.0
          }
        }
        // for (index in this.mySWIndustryValues) {
        //   indexItem = this.mySWIndustryValues[index]
        //   console.log(indexItem.name, indexItem.change)
        // }
        this.isUpdating = true
        setTimeout(() => {
          this.isUpdating = false
        }, 1500)
      },
      immediate: true,
      deep: true
    },
    swStyleValues: {
      handler (newValue, oldValue) {
        this.mySWStyleValues = this.swStyleValues
        // 计算变化值
        if (typeof (oldValue) !== 'undefined') {
          for (var index in this.mySWStyleValues) {
            var indexItem = this.mySWStyleValues[index]
            for (var oldIndex in oldValue) {
              var oldIndexItem = oldValue[oldIndex]
              if (oldIndexItem.code === indexItem.code) {
                indexItem['change'] = indexItem.current - oldIndexItem.current
                break
              }
            }
          }
        } else {
          for (index in this.mySWStyleValues) {
            indexItem = this.mySWStyleValues[index]
            indexItem['change'] = 0.0
          }
        }
        // for (index in this.mySWStyleValues) {
        //   indexItem = this.mySWStyleValues[index]
        //   console.log(indexItem.name, indexItem.change)
        // }
      },
      immediate: true,
      deep: true
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
  width: 45%;
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
  width: 1.5rem;
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
  width: 1.5rem;
  height: 0.5rem;
  font-size: 0.33rem;
  /* text-align: center; */
  color:#FFFFFF;
  background-color: #333333;
}

.index-title-center {
  justify-content: center;
}

.change-icon {
  display: flex;
  justify-content:center;
  align-items: center;
  margin: 1px;
  padding: 1px;
  width: 0.5rem;
  height: 0.5rem;
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

.normal-text-color {
  color: #FFFFFF;
}
.rise-text-color {
  color: #EE2200;
}
.fall-text-color {
  color: #00DD22;
}

.flash {
  animation: flash 1.2s;
}

@keyframes flash {
  0% { opacity: 1;}
  25% { opacity: 0;}
  50% { opacity: 1;}
  75% { opacity: 0;}
  100% {opacity: 1;}
}

</style>
