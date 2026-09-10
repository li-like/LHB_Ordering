/**
 * 日期工具函数模块
 */

/**
 * 格式化日期为易读格式
 * @param {string|Date} date 日期对象或ISO日期字符串
 * @param {string} format 格式化模式，默认为 'YYYY-MM-DD'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 获取相对日期描述
 * @param {string|Date} date 日期对象或ISO日期字符串
 * @returns {string} 相对描述（今天、明天、昨天等）
 */
export function getRelativeDate(date) {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  
  // 重置时间部分以便比较日期
  d.setHours(0, 0, 0, 0);
  today.setHours(0, 0, 0, 0);
  tomorrow.setHours(0, 0, 0, 0);
  yesterday.setHours(0, 0, 0, 0);
  
  if (d.getTime() === today.getTime()) return '今天';
  if (d.getTime() === tomorrow.getTime()) return '明天';
  if (d.getTime() === yesterday.getTime()) return '昨天';
  
  return formatDate(date);
}

/**
 * 获取两个日期之间的天数
 * @param {string|Date} startDate 开始日期
 * @param {string|Date} endDate 结束日期
 * @returns {number} 天数差
 */
export function getDaysBetween(startDate, endDate) {
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  // 重置时间部分以便计算整天差
  start.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);
  
  const diffTime = Math.abs(end - start);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
  
  return diffDays;
}

/**
 * 获取指定日期的星期几
 * @param {string|Date} date 日期对象或ISO日期字符串
 * @returns {string} 星期几
 */
export function getDayOfWeek(date) {
  const d = new Date(date);
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
  return weekdays[d.getDay()];
}

/**
 * 添加天数到指定日期
 * @param {string|Date} date 原始日期
 * @param {number} days 要添加的天数
 * @returns {string} 新的日期字符串 (YYYY-MM-DD格式)
 */
export function addDays(date, days) {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return formatDate(d);
}

/**
 * 检查日期是否是今天
 * @param {string|Date} date 日期
 * @returns {boolean} 是否是今天
 */
export function isToday(date) {
  const d = new Date(date);
  const today = new Date();
  
  return d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear();
}

/**
 * 获取当前日期字符串 (YYYY-MM-DD格式)
 * @returns {string} 今天的日期字符串
 */
export function getTodayString() {
  return formatDate(new Date());
}
