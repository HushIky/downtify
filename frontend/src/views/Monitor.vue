<template>
  <div class="min-h-screen">
    <Navbar />
    <Settings />

    <div class="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight">
          {{ t('monitor.title') }}
        </h1>
        <p class="mt-1 text-sm text-base-content/60">
          {{ t('monitor.subtitle') }}
        </p>
      </div>

      <!-- Tabs -->
      <div class="flex border-b border-white/5 mb-6">
        <button
          @click="activeTab = 'playlist'"
          class="px-4 py-2 text-sm font-medium transition-colors relative"
          :class="activeTab === 'playlist' ? 'text-primary' : 'text-base-content/60 hover:text-base-content'"
        >
          {{ t('monitor.playlistsTab') }}
          <div
            v-if="activeTab === 'playlist'"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
          />
        </button>
        <button
          @click="activeTab = 'artist'"
          class="px-4 py-2 text-sm font-medium transition-colors relative"
          :class="activeTab === 'artist' ? 'text-primary' : 'text-base-content/60 hover:text-base-content'"
        >
          {{ t('monitor.artistsTab') }}
          <div
            v-if="activeTab === 'artist'"
            class="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
          />
        </button>
      </div>

      <!-- Add form -->
      <div class="surface rounded-2xl p-5 mb-8">
        <h2
          class="text-sm font-semibold uppercase tracking-wider text-base-content/50 mb-4"
        >
          {{ activeTab === 'playlist' ? t('monitor.watchNew') : t('monitor.watchNewArtist') }}
        </h2>
        <form @submit.prevent="onAdd" class="flex flex-col sm:flex-row gap-3">
          <input
            v-model="newUrl"
            type="text"
            :placeholder="activeTab === 'playlist' ? t('monitor.urlPlaceholder') : t('monitor.artistUrlPlaceholder')"
            class="input-modern flex-1 h-11 text-sm"
            :disabled="adding"
          />
          <div class="flex items-center gap-2 shrink-0">
            <select
              v-model="newInterval"
              class="select select-sm rounded-full border border-white/10 bg-base-100/85 focus:border-primary/60 h-11 px-3 text-sm"
              :disabled="adding"
            >
              <option :value="15">{{ t('monitor.every15') }}</option>
              <option :value="30">{{ t('monitor.every30') }}</option>
              <option :value="60">{{ t('monitor.every1h') }}</option>
              <option :value="180">{{ t('monitor.every3h') }}</option>
              <option :value="360">{{ t('monitor.every6h') }}</option>
              <option :value="720">{{ t('monitor.every12h') }}</option>
              <option :value="1440">{{ t('monitor.every1d') }}</option>
              <option :value="10080">{{ t('monitor.every1w') }}</option>
              <option :value="20160">{{ t('monitor.every2w') }}</option>
              <option :value="43200">{{ t('monitor.every1mo') }}</option>
            </select>
            <button
              type="submit"
              class="btn btn-primary btn-sm h-11 px-5 rounded-full"
              :disabled="adding || !newUrl.trim()"
            >
              <span v-if="adding" class="loading loading-spinner loading-xs" />
              <span v-else>{{ t('monitor.watch') }}</span>
            </button>
          </div>
        </form>
        <p v-if="addError" class="mt-2 text-xs text-error">{{ addError }}</p>
      </div>

      <!-- Loading skeleton -->
      <div v-if="loading" class="space-y-3">
        <div v-for="n in 3" :key="n" class="skeleton h-24 rounded-2xl" />
      </div>

      <!-- Empty state -->
      <div
        v-else-if="activeTab === 'playlist' && playlists.length === 0"
        class="surface rounded-2xl p-12 flex flex-col items-center text-center"
      >
        <Icon
          icon="clarity:music-note-line"
          class="h-12 w-12 text-base-content/20 mb-4"
        />
        <p class="text-base-content/50 text-sm">
          {{ t('monitor.empty') }}
        </p>
        <p class="text-base-content/40 text-xs mt-1">
          {{ t('monitor.emptyHint') }}
        </p>
      </div>

      <div
        v-else-if="activeTab === 'artist' && artists.length === 0"
        class="surface rounded-2xl p-12 flex flex-col items-center text-center"
      >
        <Icon
          icon="clarity:music-note-line"
          class="h-12 w-12 text-base-content/20 mb-4"
        />
        <p class="text-base-content/50 text-sm">
          {{ t('monitor.emptyArtist') }}
        </p>
        <p class="text-base-content/40 text-xs mt-1">
          {{ t('monitor.emptyArtistHint') }}
        </p>
      </div>

      <!-- Playlist/Artist cards -->
      <ul v-else class="space-y-3">
        <!-- Playlists -->
        <template v-if="activeTab === 'playlist'">
          <li
            v-for="pl in playlists"
            :key="pl.id"
            class="surface rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4"
          >
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold truncate">{{ pl.name }}</span>
                <span
                  class="pill shrink-0"
                  :class="pl.enabled ? 'badge-soft' : 'badge-neutral-soft'"
                >
                  {{ pl.enabled ? t('monitor.active') : t('monitor.paused') }}
                </span>
              </div>
              <div
                class="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-base-content/50"
              >
                <span>
                  <Icon
                    icon="clarity:refresh-line"
                    class="inline h-3 w-3 mr-0.5"
                  />
                  {{
                    t('monitor.everyInterval', {
                      interval: formatInterval(pl.interval_minutes),
                    })
                  }}
                </span>
                <span>
                  <Icon
                    icon="clarity:music-note-line"
                    class="inline h-3 w-3 mr-0.5"
                  />
                  {{
                    pl.last_track_count === 1
                      ? t('monitor.tracksOne', { count: pl.last_track_count })
                      : t('monitor.tracksMany', { count: pl.last_track_count })
                  }}
                </span>
                <span v-if="pl.last_checked">
                  <Icon icon="clarity:clock-line" class="inline h-3 w-3 mr-0.5" />
                  {{ t('monitor.checked', { when: timeAgo(pl.last_checked) }) }}
                </span>
                <span v-else class="italic">{{ t('monitor.notChecked') }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 shrink-0">
              <select
                :value="pl.interval_minutes"
                @change="onChangeInterval(pl, 'playlist', $event)"
                class="select select-xs rounded-full border border-white/10 bg-base-100/60 text-xs focus:border-primary/60"
              >
                <option :value="15">{{ t('monitor.short15') }}</option>
                <option :value="30">{{ t('monitor.short30') }}</option>
                <option :value="60">{{ t('monitor.short1h') }}</option>
                <option :value="180">{{ t('monitor.short3h') }}</option>
                <option :value="360">{{ t('monitor.short6h') }}</option>
                <option :value="720">{{ t('monitor.short12h') }}</option>
                <option :value="1440">{{ t('monitor.short1d') }}</option>
                <option :value="10080">{{ t('monitor.short1w') }}</option>
                <option :value="20160">{{ t('monitor.short2w') }}</option>
                <option :value="43200">{{ t('monitor.short1mo') }}</option>
              </select>

              <button
                class="icon-btn"
                :title="pl.enabled ? t('monitor.pause') : t('monitor.resume')"
                @click="onToggle(pl, 'playlist')"
              >
                <Icon
                  :icon="pl.enabled ? 'clarity:pause-line' : 'clarity:play-line'"
                  class="h-4 w-4"
                />
              </button>

              <button
                class="icon-btn"
                :title="t('monitor.checkNow')"
                :disabled="checking[pl.id]"
                @click="onCheck(pl, 'playlist')"
              >
                <span
                  v-if="checking[pl.id]"
                  class="loading loading-spinner loading-xs"
                />
                <Icon v-else icon="clarity:refresh-line" class="h-4 w-4" />
              </button>

              <button
                class="icon-btn text-error/70 hover:text-error hover:bg-error/10"
                :title="t('monitor.stop')"
                @click="onDelete(pl, 'playlist')"
              >
                <Icon icon="clarity:trash-line" class="h-4 w-4" />
              </button>
            </div>
          </li>
        </template>

        <!-- Artists -->
        <template v-else>
          <li
            v-for="art in artists"
            :key="art.id"
            class="surface rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center gap-4"
          >
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold truncate">{{ art.name }}</span>
                <span
                  class="pill shrink-0"
                  :class="art.enabled ? 'badge-soft' : 'badge-neutral-soft'"
                >
                  {{ art.enabled ? t('monitor.active') : t('monitor.paused') }}
                </span>
              </div>
              <div
                class="flex flex-wrap gap-x-4 gap-y-0.5 text-xs text-base-content/50"
              >
                <span>
                  <Icon
                    icon="clarity:refresh-line"
                    class="inline h-3 w-3 mr-0.5"
                  />
                  {{
                    t('monitor.everyInterval', {
                      interval: formatInterval(art.interval_minutes),
                    })
                  }}
                </span>
                <span v-if="art.last_checked">
                  <Icon icon="clarity:clock-line" class="inline h-3 w-3 mr-0.5" />
                  {{ t('monitor.checked', { when: timeAgo(art.last_checked) }) }}
                </span>
                <span v-else class="italic">{{ t('monitor.notChecked') }}</span>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-2 shrink-0">
              <select
                :value="art.interval_minutes"
                @change="onChangeInterval(art, 'artist', $event)"
                class="select select-xs rounded-full border border-white/10 bg-base-100/60 text-xs focus:border-primary/60"
              >
                <option :value="15">{{ t('monitor.short15') }}</option>
                <option :value="30">{{ t('monitor.short30') }}</option>
                <option :value="60">{{ t('monitor.short1h') }}</option>
                <option :value="180">{{ t('monitor.short3h') }}</option>
                <option :value="360">{{ t('monitor.short6h') }}</option>
                <option :value="720">{{ t('monitor.short12h') }}</option>
                <option :value="1440">{{ t('monitor.short1d') }}</option>
                <option :value="10080">{{ t('monitor.short1w') }}</option>
                <option :value="20160">{{ t('monitor.short2w') }}</option>
                <option :value="43200">{{ t('monitor.short1mo') }}</option>
              </select>

              <button
                class="icon-btn"
                :title="art.enabled ? t('monitor.pause') : t('monitor.resume')"
                @click="onToggle(art, 'artist')"
              >
                <Icon
                  :icon="art.enabled ? 'clarity:pause-line' : 'clarity:play-line'"
                  class="h-4 w-4"
                />
              </button>

              <button
                class="icon-btn"
                :title="t('monitor.checkNow')"
                :disabled="checking[art.id]"
                @click="onCheck(art, 'artist')"
              >
                <span
                  v-if="checking[art.id]"
                  class="loading loading-spinner loading-xs"
                />
                <Icon v-else icon="clarity:refresh-line" class="h-4 w-4" />
              </button>

              <button
                class="icon-btn text-error/70 hover:text-error hover:bg-error/10"
                :title="t('monitor.stop')"
                @click="onDelete(art, 'artist')"
              >
                <Icon icon="clarity:trash-line" class="h-4 w-4" />
              </button>
            </div>
          </li>
        </template>
      </ul>

      <!-- Info banner -->
      <div
        class="mt-8 surface rounded-2xl p-4 flex gap-3 text-sm text-base-content/60"
      >
        <Icon
          icon="clarity:info-standard-line"
          class="h-5 w-5 shrink-0 mt-0.5 text-primary/70"
        />
        <p>{{ activeTab === 'playlist' ? t('monitor.info') : t('monitor.infoArtist') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import Navbar from '/src/components/Navbar.vue'
import Settings from '/src/components/Settings.vue'
import monitorAPI from '/src/model/monitor.js'
import { useI18n } from '/src/i18n'

const { t } = useI18n()

const activeTab = ref('playlist')
const playlists = ref([])
const artists = ref([])
const loading = ref(false)
const adding = ref(false)
const addError = ref('')
const newUrl = ref('')
const newInterval = ref(60)
const checking = ref({})

async function load() {
  loading.value = true
  try {
    const [plRes, artRes] = await Promise.all([
      monitorAPI.listMonitoredPlaylists(),
      monitorAPI.listMonitoredArtists(),
    ])
    playlists.value = plRes.data || []
    artists.value = artRes.data || []
  } finally {
    loading.value = false
  }
}

async function onAdd() {
  addError.value = ''
  adding.value = true
  try {
    if (activeTab.value === 'playlist') {
      const res = await monitorAPI.addMonitoredPlaylist(
        newUrl.value.trim(),
        newInterval.value
      )
      playlists.value.unshift(res.data)
    } else {
      const res = await monitorAPI.addMonitoredArtist(
        newUrl.value.trim(),
        newInterval.value
      )
      artists.value.unshift(res.data)
    }
    newUrl.value = ''
  } catch (e) {
    addError.value = e?.response?.data?.detail || 
      (activeTab.value === 'playlist' ? t('monitor.failedAdd') : t('monitor.failedAddArtist'))
  } finally {
    adding.value = false
  }
}

async function onToggle(item, type = 'playlist') {
  try {
    if (type === 'playlist') {
      const res = await monitorAPI.updateMonitoredPlaylist(item.id, {
        enabled: !item.enabled,
      })
      Object.assign(item, res.data)
    } else {
      const res = await monitorAPI.updateMonitoredArtist(item.id, {
        enabled: !item.enabled,
      })
      Object.assign(item, res.data)
    }
  } catch {
    // silently ignore
  }
}

async function onChangeInterval(item, type, event) {
  const val = parseInt(event.target.value, 10)
  try {
    if (type === 'playlist') {
      const res = await monitorAPI.updateMonitoredPlaylist(item.id, {
        interval_minutes: val,
      })
      Object.assign(item, res.data)
    } else {
      const res = await monitorAPI.updateMonitoredArtist(item.id, {
        interval_minutes: val,
      })
      Object.assign(item, res.data)
    }
  } catch {
    // silently ignore
  }
}

async function onCheck(item, type = 'playlist') {
  checking.value = { ...checking.value, [item.id]: true }
  try {
    if (type === 'playlist') {
      await monitorAPI.checkMonitoredPlaylist(item.id)
    } else {
      await monitorAPI.checkMonitoredArtist(item.id)
    }
    setTimeout(async () => {
      try {
        if (type === 'playlist') {
          const res = await monitorAPI.listMonitoredPlaylists()
          playlists.value = res.data || []
        } else {
          const res = await monitorAPI.listMonitoredArtists()
          artists.value = res.data || []
        }
      } finally {
        checking.value = { ...checking.value, [item.id]: false }
      }
    }, 3000)
  } catch {
    checking.value = { ...checking.value, [item.id]: false }
  }
}

async function onDelete(item, type = 'playlist') {
  const promptMsg = type === 'playlist'
    ? t('monitor.deletePrompt', { name: item.name })
    : t('monitor.deleteArtistPrompt', { name: item.name })
  if (!confirm(promptMsg)) return
  try {
    if (type === 'playlist') {
      await monitorAPI.deleteMonitoredPlaylist(item.id)
      playlists.value = playlists.value.filter((p) => p.id !== item.id)
    } else {
      await monitorAPI.deleteMonitoredArtist(item.id)
      artists.value = artists.value.filter((a) => a.id !== item.id)
    }
  } catch {
    // silently ignore
  }
}

function formatInterval(minutes) {
  if (minutes < 60) return `${minutes} ${t('monitor.minSuffix')}`
  if (minutes < 1440) return `${minutes / 60} ${t('monitor.hourSuffix')}`
  if (minutes < 10080) {
    const days = minutes / 1440
    return `${days} ${days === 1 ? t('monitor.daySuffix') : t('monitor.daysSuffix')}`
  }
  if (minutes < 43200) {
    const weeks = minutes / 10080
    return `${weeks} ${weeks === 1 ? t('monitor.weekSuffix') : t('monitor.weeksSuffix')}`
  }
  const months = Math.round(minutes / 43200)
  return `${months} ${months === 1 ? t('monitor.monthSuffix') : t('monitor.monthsSuffix')}`
}

function timeAgo(isoString) {
  try {
    const diff = Date.now() - new Date(isoString).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return t('monitor.timeJustNow')
    if (mins < 60) return t('monitor.timeMinAgo', { n: mins })
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return t('monitor.timeHourAgo', { n: hrs })
    return t('monitor.timeDayAgo', { n: Math.floor(hrs / 24) })
  } catch {
    return ''
  }
}

onMounted(load)
</script>
