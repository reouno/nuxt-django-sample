<template>
  <div>
    <v-row>
      <v-col>
        <v-card v-if="isLoggedIn">
          <v-card-title>ログイン済み</v-card-title>
          <v-card-text>
            <p>メール: {{ user.email }}</p>
          </v-card-text>
          <v-btn @click="logout">ログアウト</v-btn>
        </v-card>
        <v-card v-else>
          <v-card-title>ログイン</v-card-title>
          <v-card-text>
            <v-form>
              <v-text-field
                v-model="email"
              ></v-text-field>
              <v-text-field
                v-model="password"
              ></v-text-field>
            </v-form>
            <v-btn @click="login">ログイン</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import {Component, Vue} from "nuxt-property-decorator"

@Component
export default class Sample extends Vue {
  email: string = 'admin@example.com'
  password: string = 'test1234test'

  user: any = null

  async created() {
    await this.getCsrfToken()
    await this.fetchUser()
  }

  get isLoggedIn(): boolean {
    return this.user !== null
  }

  getCsrfToken() {
    this.$axios.get('/api/accounts/set-csrf/')
  }

  login() {
    this.$axios.post('/api/accounts/login/', {
      email: this.email,
      password: this.password,
    }).then((response) => {
      console.log('ログインレスポンス', response)
      this.fetchUser()
    }).catch((error) => {
      console.error('ログイン失敗', error)
    })
  }

  logout() {
    this.$axios.post('/api/accounts/logout/').then((r) => {
      console.log('ログアウトしました')
    }).catch((e) => {
      console.error('ログアウト中にエラーが発生しました')
    }).finally(() => {
      this.clearUserData()
    })
  }

  fetchUser() {
    this.$axios.get('/api/accounts/detail/').then((r) => {
      this.user = r.data.user
    }).catch((e) => {
      console.log('未ログイン状態です')
      this.user = null
    })
  }

  clearUserData() {
    this.user = null
  }
}
</script>
