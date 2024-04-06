import os

from ai_datahive.dao import BaseDAO, SupabaseDAO


def get_dao() -> BaseDAO:
    dao_impl = os.getenv('DAO_IMPL', 'supabase')
    if dao_impl == 'supabase':
        return SupabaseDAO()
    else:
        return SupabaseDAO()
