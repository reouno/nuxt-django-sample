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
    <v-row>
      <v-col>
        <v-textarea
          v-model="content"
        ></v-textarea>
        <v-btn @click="onClickCreateNote">作成</v-btn>
      </v-col>
    </v-row>
    <v-row v-if="!editing">
      <v-col>
        <v-card v-for="elem in notes" :key="elem.id">
          <v-card-text>
            {{ elem.content }}
          </v-card-text>
          <v-btn @click="editNote(elem)">編集</v-btn>
          <v-btn @click="onClickDeleteNote(elem)">削除</v-btn>
          <v-divider class="my-1" :key="elem.id"></v-divider>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-else-if="editingNote !== null">
      <v-col>
        <p>ノートID: {{ editingNote.id }}</p>
        <v-textarea
          v-model="editingNote.content"
        ></v-textarea>
        <v-btn @click="onClickSaveNote">保存</v-btn>
        <v-btn @click="onClickDeleteNote(editingNote)">削除</v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn @click="emptyDict204">DELETE 空Dict204</v-btn>
        <v-btn @click="empty204">DELETE 空204</v-btn>
        <v-btn @click="emptyDict200">DELETE 空Dict200</v-btn>
        <v-btn @click="empty200">DELETE 空200</v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import {Component, Vue} from "nuxt-property-decorator"

interface Note {
  id: string
  content: string
}

@Component
export default class Sample extends Vue {
  email: string = 'admin@example.com'
  password: string = ''

  user: any = null

  notes: Note[] = []

  editing: boolean = false
  editingNote: Note | null = null

  content: string = ''

  // isLoading: boolean = true

  async created() {
    // this.isLoading = true
    this.editing = false
    this.editingNote = null
    this.content = ''
    this.user = null

    await this.getCsrfToken()
    await this.fetchUser()
    await this.listNotes()
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

  listNotes() {
    this.$axios.get('/api/notes/notes/').then((r) => {
      this.notes = r.data.notes
    }).catch((e) => {
      console.error('ノートリストを取得できなかった', e)
    })
  }

  createNote() {
    if (this.content.length === 0) {
      console.log('ノートは未作成です')

      return
    }

    this.$axios.post('/api/notes/notes/', {
      'id': '0',
      'content': this.content,
    }).then((r) => {
      console.log('ノート作成しました')
    }).catch((e) => {
      console.error('ノート作成できなかった', e)
    })
  }

  updateNote() {
    if (this.editingNote === null) {
      console.log('ノートは未選択・未編集です')

      return
    }

    this.$axios.put(`/api/notes/notes/${this.editingNote.id}`, this.editingNote).then((r) => {
      console.log('ノート編集しました')
    }).catch((e) => {
      console.error('ノート編集できなかった', e)
    }).finally(() => {
      this.editingNote = null
    })
  }

  deleteNote() {
    if (this.editingNote === null) {
      console.log('ノートは未選択です')

      return
    }

    this.$axios.delete(`/api/notes/notes/${this.editingNote.id}`).then((r) => {
      console.log('ノート削除し増田')
    }).catch((e) => {
      console.error('ノート削除できなかった', e)
    }).finally(() => {
      this.editingNote = null
    })
  }

  async onClickCreateNote() {
    await this.createNote()
    await this.listNotes()
    this.content = ''
  }

  editNote(note: Note) {
    this.editingNote = note
    this.editing = true
  }

  async onClickSaveNote() {
    await this.updateNote()
    await this.listNotes()
    this.editing = false
  }

  async onClickDeleteNote(note: Note) {
    this.editingNote = note
    await this.deleteNote()
    await this.listNotes()
    this.editing = false
  }

  emptyDict204() {
    this.$axios.get('/api/accounts/empty-dict-204/')
  }

  empty204() {
    this.$axios.get('/api/accounts/empty-204/')
  }

  emptyDict200() {
    this.$axios.get('/api/accounts/empty-dict-200/')
  }

  empty200() {
    this.$axios.get('/api/accounts/empty-200/')
  }
}
</script>
