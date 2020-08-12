import Vue from 'vue'
import Router from 'vue-router'
import IndexValueComponent from '@/components/IndexValueComponent'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'IndexValueComponent',
      component: IndexValueComponent
    }
  ]
})
