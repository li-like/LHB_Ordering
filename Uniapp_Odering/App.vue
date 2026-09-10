<script>
export default { onLaunch() {
  // #ifdef MP-WEIXIN
  uni.setNavigationBarColor({ frontColor: '#000000', backgroundColor: '#F8F2E8' })
  // #endif
} }
</script>
<style lang="scss">
@import './uni.scss';
page { min-height: 100%; background: #F8F2E8; color: #2F2925; font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
view, text, button, input, textarea { box-sizing: border-box; } button { border: 0; }
.safe-top { padding-top: env(safe-area-inset-top); } .safe-bottom { padding-bottom: env(safe-area-inset-bottom); }.safe-page { width: 100%; }
.v2-card { position: relative; border-radius: var(--card-radius, 20px); box-shadow: 0 9px 28px rgba(74, 55, 43, .08); }
.cards-outline .v2-card { box-shadow: none; border: 1px solid rgba(47, 41, 37, .14); }
.cards-glass .v2-card { background-color: rgba(255, 255, 255, .68) !important; backdrop-filter: blur(14px); }
@media (min-width: 960px) { page { background: #F3ECE2; } }
</style>
