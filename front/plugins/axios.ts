import { NuxtAxiosInstance } from '@nuxtjs/axios'
import Cookies from 'js-cookie'

export default function ({ $axios }: { $axios: NuxtAxiosInstance }) {
  // $axios.defaults.xsrfHeaderName = 'X-CSRFToken'
  // $axios.defaults.xsrfCookieName = 'csrftoken'

  $axios.onRequest((config) => {
    if (Cookies.get('csrftoken')) {
      config.headers.common['X-CSRFToken'] = Cookies.get('csrftoken')
    }

    return config
  })
}
