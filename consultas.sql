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

