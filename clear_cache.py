#!/usr/bin/env python3
"""
Скрипт для очистки кеша Redis
"""

import asyncio
import os
from redis_cache import get_redis_client, close_redis_client

async def clear_cache():
    """Очистить весь кеш Redis"""
    try:
        redis_client = await get_redis_client()
        
        # Получить все ключи
        keys = await redis_client.keys("*")
        
        if keys:
            # Удалить все ключи
            await redis_client.delete(*keys)
            print(f"✅ Очищено {len(keys)} ключей из кеша")
        else:
            print("ℹ️ Кеш уже пуст")
            
    except Exception as e:
        print(f"❌ Ошибка при очистке кеша: {e}")
    finally:
        await close_redis_client()

async def show_cache_stats():
    """Показать статистику кеша"""
    try:
        redis_client = await get_redis_client()
        
        # Получить все ключи
        keys = await redis_client.keys("*")
        
        print(f"📊 Статистика кеша:")
        print(f"   Всего ключей: {len(keys)}")
        
        if keys:
            # Группировать ключи по префиксу
            key_groups = {}
            for key in keys:
                prefix = key.split(':')[0] if ':' in key else 'other'
                key_groups[prefix] = key_groups.get(prefix, 0) + 1
            
            print(f"   Группы ключей:")
            for prefix, count in key_groups.items():
                print(f"     {prefix}: {count}")
                
            # Показать несколько примеров ключей
            print(f"   Примеры ключей:")
            for key in keys[:5]:
                ttl = await redis_client.ttl(key)
                print(f"     {key} (TTL: {ttl}s)")
            if len(keys) > 5:
                print(f"     ... и еще {len(keys) - 5} ключей")
        else:
            print("   Кеш пуст")
            
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
    finally:
        await close_redis_client()

async def main():
    """Главная функция"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        await show_cache_stats()
    else:
        print("🧹 Очистка кеша Redis...")
        await clear_cache()
        print("✅ Готово!")

if __name__ == "__main__":
    asyncio.run(main()) 