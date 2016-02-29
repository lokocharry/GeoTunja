--Rutas más cercana a evento
SELECT b.the_geom, nn(a.the_geom,0.00001,2,100,'rutas_tunja','id','the_geom')
FROM evento_ruta as a, rutas_tunja as b
GROUP BY a.the_geom, b.id
HAVING b.id=nn(a.the_geom,0.00001,2,100,'rutas_tunja','id','the_geom');

--Ruta con restricciones de giro
select * from pgr_trsp(
     'select id as id, source, target, cost, reverse_cost from rutas_tunja',
     4, 11, true, true, 
     'select to_cost, target_id, via_path from restricciones');

--Ruta con restricciones de giro y evitando rutas con eventos
select * from pgr_trsp(
     'select id as id, source, target, cost, reverse_cost from rutas_tunja
     where id not in (SELECT nn(a.the_geom,0.00001,2,100) as id
			FROM evento_ruta as a, rutas_tunja as b
			GROUP BY a.the_geom, b.id
			HAVING b.id=nn(a.the_geom,0.00001,2,100))',
     4, 11, true, true, 
     'select to_cost, target_id, via_path from restricciones');

--Ruta sin restricciones de giro y evitando rutas con eventos
select * from pgr_astar(
     'select id as id, source, target, cost, reverse_cost, x1, y1, x2, y2 from rutas_tunja
     where id not in (SELECT nn(a.the_geom,0.00001,2,100) as id
			FROM evento_ruta as a, rutas_tunja as b
			GROUP BY a.the_geom, b.id
			HAVING b.id=nn(a.the_geom,0.00001,2,100))',
     4, 11, true, true);

--Función de vecino más cercano
create or replace function 
  nn(nearTo                   geometry
   , initialDistance          real
   , distanceMultiplier       real 
   , maxPower                 integer)
 returns integer as $$
declare 
  sql     text;
  result  integer;
begin
  sql := ' select id' 
      || ' from rutas_tunja'
      || ' where st_dwithin($1, ' 
      ||   'the_geom' || ', $2 * ($3 ^ $4))'
      || ' order by st_distance($1, ' || 'the_geom' || ')'
      || ' limit 1';
  for i in 0..maxPower loop
     execute sql into result using nearTo              -- $1
                                , initialDistance     -- $2
                                , distanceMultiplier  -- $3
                                , i;                  -- $4
    if result is not null then return result; end if;
  end loop;
  return null;
end
$$ language 'plpgsql' stable;