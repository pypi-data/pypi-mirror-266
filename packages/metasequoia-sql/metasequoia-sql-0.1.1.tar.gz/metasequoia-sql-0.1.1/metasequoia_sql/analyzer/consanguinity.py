"""
Hive 元数据：https://cloud.tencent.com/developer/article/2154682

DDL 构造语法：
```sql
select concat('create table ',t.tbl_name,' (\n',c.col_string,')',
  case pk.partition_string WHEN NULL then NULL ELSE concat('\npartition by (',pk.partition_string,')') end,
  case se.slib when null then null else concat('\nrow format serde\n''',se.slib,'''\n') end,
  case sep.serde_id when null then null else concat('WITH SERDEPROPERTIES (\n',sep.params,')\n') end,
  'stored as inputformat\n''',
  s.input_format,'''\noutputformat\n''',
  s.output_format,'\nlocation\n''',s.location,''';'
) as ddl_sql
from TBLS t
left join (select tbl_id,group_concat(concat_ws(' ',pkey_name,pkey_type,concat("'",PKEY_COMMENT,"'"))) as partition_string from PARTITION_KEYS group by tbl_id order by integer_idx) pk on t.tbl_id = pk.tbl_id
left join DBS d on t.db_id = d.db_id
left join SDS s on t.sd_id = s.sd_id
left join SERDES se on s.serde_id = se.serde_id
left join (select serde_id,group_concat(concat_ws('=',concat('''',param_key,''''),concat('''',param_value,'''\n'))) params from SERDE_PARAMS group by serde_id) sep on se.serde_id = sep.serde_id
left join (select cd_id, group_concat(concat_ws(' ',column_name,type_name,"comment",concat("'",comment,"'")) separator ',\n') as col_string from COLUMNS_V2 group by cd_id order by integer_idx) c on s.cd_id = c.cd_id
WHERE t.TBL_NAME = 'company_shareholder_information'
-- and t.owner = ''
-- and d.name = ''
group by  d.name, t.owner,t.tbl_name;
```

"""