CREATE OR REPLACE FUNCTION xml_directions(source_id integer, target_id
integer, tab_name text)
  RETURNS xml AS
$BODY$
DECLARE

start_point geometry; --geometria del punto iniziale
tab_name text :=$3; -- nome della tabella (ways)
s_id integer :=$1; -- source id
t_id integer :=$2; -- target id
_first boolean :=true; --è il primo step dell'algoritmo
fc real:= 111073.2835905824; -- fattore conversione moltiplicativo per le distanze
_A geometry;
_B geometry;
_C geometry;
_D geometry;
a1 float; -- azimuth fine prima geometria
a2 float; -- azimuth inizio seconda geometria
angoli real[]; -- array degli angoli (differenza) da restituire
i integer; -- intero per scorrere l'array - NB è definito fuori dal loop perchè serve anche per ottenere la lunghezza degli array

the_route CURSOR FOR SELECT b.id, b.the_geom, b.km, b.osm_name FROM pgr_astar('
                SELECT id AS id,
                         source::integer,
                         target::integer,
                         x1,
                         y1,
                         x2,
                         y2,
                         cost::double precision AS cost,
                         reverse_cost
                        FROM rutas_tunja',
                s_id, t_id, true, true) as a, rutas_tunja as b
                WHERE b.id=a.id2;
--variabili per il fetch
GID_1 integer;
GID_2 integer;
GEOM_1 geometry;
GEOM_2 geometry;
LENGTH_1 real;
LENGTH_2 real;
NAME_1 text;
NAME_2 text;


directions text[]; --vettore contenente i codici relaivi alle manovre
lengths real[]; --vettore contenente le lunghezze dei tratti da percorrere
streets text[]; --vettore contenente i nomi dele strade della rotta
geoms geometry[]; --vettore delle singole geometrie
line geometry; --geometria complessiva della rotta
tot_len real :=0;
tot_time real:=0;
tlu text := 'm'; -- total length units

-- var per l'execute della query per la composizione dell'xml
pre_string text;


steps_fragment text:='XMLELEMENT(NAME step,XMLELEMENT(NAME text,''Inicia en
';
line_fragment text;

xml_result xml;

BEGIN

angoli[0] :=0; -- la prima indicazione è sempre "procedi su via ..." . Il riempimento del vettore angoli deve partire da angoli[1]
i:=0;
OPEN the_route;
FETCH the_route INTO GID_1, GEOM_1, LENGTH_1, NAME_1;
 IF NAME_1 IS NOT NULL THEN
streets[0]:= replace(trim(both from NAME_1),'''','''''');
ELSE streets[0]:='Missing Street Name';
END IF;
 lengths[0]:= LENGTH_1*fc;
--tot_len := tot_len + lengths[0];
line:=ST_Union(GEOM_1);
RAISE NOTICE ' STREET [0] = %',streets[0];
RAISE NOTICE ' LENGTHS [0] = %',lengths[0];
LOOP
FETCH the_route INTO GID_2, GEOM_2, LENGTH_2, NAME_2;
EXIT WHEN NOT FOUND;

-- caso primo segmento
 IF _first THEN
-- devo capire chi è il punto iniziale
_A :=ST_PointN(GEOM_1,1);
_B :=ST_PointN(GEOM_1,ST_NumPoints(GEOM_1));
_C :=ST_PointN(GEOM_2,1);
_D :=ST_PointN(GEOM_2,ST_NumPoints(GEOM_2));
IF (ST_Equals(_A, _C)) THEN
start_point := _B;
 ELSIF (ST_Equals(_A, _D)) THEN
start_point := _B;
 ELSE
start_point := _A;
 END IF;
 --valuto quale endpoint della prima geometria è connessa allo startpoint ese necessario flippo la geometria
IF NOT(ST_Equals(start_point,ST_PointN(GEOM_1,1))) THEN -- lo start point non coincide con il primo punto del primo segmento, quindi il segmento va flippato
GEOM_1 := ST_Reverse(GEOM_1);
 END IF;
geoms[i]:= GEOM_1;
 start_point:= ST_PointN(Geom_1,ST_NumPoints(GEOM_1)); --aggiorno lo start point come l'ultimo punto della prima geometria

--valuto quale endpoint della seconda geometria è connessa all'ultimo punto della prima geometria (che è già stata correttamente orientata) e se necessario flippo la seconda geometria
IF NOT(ST_Equals(start_point, ST_PointN(GEOM_2,1))) THEN
GEOM_2 := ST_Reverse(GEOM_2);
 END IF;
start_point:= ST_PointN(Geom_2,ST_NumPoints(GEOM_2)); -- aggiorno lo start point per lo step successivo del loop

-- i segmenti sono orientati; calcolo gli azimuth e definisco la direzione
a1 :=
trunc(ST_Azimuth(ST_PointN(GEOM_1,ST_NumPoints(GEOM_1)-1),ST_PointN(GEOM_1,ST_NumPoints(GEOM_1)))/(2*pi())*360);
 a2 :=
trunc(ST_Azimuth(ST_PointN(GEOM_2,1),ST_PointN(GEOM_2,2))/(2*pi())*360);
 -- la differenza di questi angoli definisce la manovra da effettuare, quindi VA RITORNATA IN QUALCHE MODO
angoli[i+1] := (a1 - a2);
IF (angoli[i+1] >180.0) THEN angoli[i+1]:=angoli[i+1]-360;
END IF;
IF (angoli[i+1]< -180) THEN angoli[i+1]:=angoli[i+1]+360;
END IF;
IF NAME_2 IS NOT NULL THEN
streets[i+1]:= replace(trim(both from NAME_2),'''','''''');
ELSE
streets[i+1]:='nome strada mancante';
END IF;
 -- Se le strade hanno lo stesso nome
 IF ((streets[i+1] =streets[i])) THEN
 geoms[i]:=ST_Union(geoms[i],GEOM_2);
lengths[i]:=lengths[i]+(LENGTH_2 * fc);
line:=ST_Union(line,GEOM_2);
GEOM_1 := GEOM_2;
NAME_1 := NAME_2;
 ELSE
lengths[i+1]:= LENGTH_2 * fc;
 geoms[i+1]:= GEOM_2;
line:=ST_Union(line,GEOM_2);

i:= i+1;
 GID_1 := GID_2;
GEOM_1 := GEOM_2;
LENGTH_1 := LENGTH_2 * fc;
NAME_1 := NAME_2;
END IF;
 _first := false;

-- caso segmenti successivi al primo (la prima geometria è già orientata)
ELSE
IF NOT(ST_Equals(start_point, ST_PointN(GEOM_2,1))) THEN
GEOM_2 := ST_Reverse(GEOM_2);
 END IF;
start_point:= ST_PointN(Geom_2,ST_NumPoints(GEOM_2)); -- aggiorno lo start point per lo step successivo del loop

-- i segmenti sono orientati; calcolo gli azimuth e definisco la direzione
a1 :=
trunc(ST_Azimuth(ST_PointN(GEOM_1,ST_NumPoints(GEOM_1)-1),ST_PointN(GEOM_1,ST_NumPoints(GEOM_1)))/(2*pi())*360);
 a2 :=
trunc(ST_Azimuth(ST_PointN(GEOM_2,1),ST_PointN(GEOM_2,2))/(2*pi())*360);
 -- la differenza di questi angoli definisce la manovra da effettuare, quindi VA RITORNATA IN QUALCHE MODO
 angoli[i+1] := (a1 - a2);
IF (angoli[i+1] >180) THEN angoli[i+1]:=angoli[i+1]-360;
END IF;
IF (angoli[i+1]< -180) THEN angoli[i+1]:=angoli[i+1]+360;
END IF;

IF NAME_2 IS NOT NULL THEN
streets[i+1]:= replace(trim(both from NAME_2),'''','''''');
ELSE
streets[i+1]:='nome strada mancante';
END IF;

-- Se le strade hanno lo stesso nome
IF ( (streets[i+1] =streets[i])) THEN
 geoms[i]:=ST_Union(geoms[i],GEOM_2);
lengths[i]:=lengths[i]+(LENGTH_2 * fc);
line:=ST_Union(line,GEOM_2);
GEOM_1 := GEOM_2;
NAME_1 := NAME_2;

ELSE


lengths[i+1]:= LENGTH_2 * fc;
--tot_len := tot_len + lengths[i+1];
geoms[i+1]:=GEOM_2;

line:=ST_Union(line,GEOM_2);
 i:= i+1;
--GID_1 := GID_2;
GEOM_1 := GEOM_2;
--LENGTH_1 := LENGTH_2 * fc;
NAME_1 := NAME_2;
END IF;

END IF;

END LOOP;
  CLOSE the_route;

--codifico gli angoli in manovre
for k in 0..i LOOP
CASE
WHEN angoli[k]>=-5 AND angoli[k]<=5 THEN
directions[k]:='Siga derecho por';
RAISE NOTICE'RAMO 1    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>=-45 AND angoli[k]<-5 THEN
directions[k]:='A la derecha hacia';
RAISE NOTICE'RAMO 2    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>=-100 AND angoli[k]<-45 THEN
directions[k]:='Gire a la derecha en';
RAISE NOTICE'RAMO 3    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>=-135 AND angoli[k]<-100 THEN
directions[k]:='Curva a la derecha en';
RAISE NOTICE'RAMO 4    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>=-180 AND angoli[k]<-135 THEN
directions[k]:='Gire en U a la derecha en';
RAISE NOTICE'RAMO 5    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>5 AND angoli[k]<=45 THEN
directions[k]:='A la izquierda hacia';
RAISE NOTICE'RAMO 6    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>45 AND angoli[k]<=100 THEN
directions[k]:='Gire a la izquierda en';
RAISE NOTICE'RAMO 7    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>100 AND angoli[k]<=135 THEN
directions[k]:='Curva a la izquierda en';
RAISE NOTICE'RAMO 8    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
WHEN angoli[k]>135 AND angoli[k]<=180 THEN
directions[k]:='Gire en U a la izquierda en';
RAISE NOTICE'RAMO 9    %',directions[k];
RAISE NOTICE'RAMO 1    %',geoms[k];
ELSE RAISE NOTICE' ELSE%',directions[k];
END CASE;
tot_len := tot_len + lengths[k];
END LOOP;
tot_len := trunc(tot_len);
tot_time := trunc(tot_len/833.33333); -- si assume velocità media di 50 km/h

IF (tot_len >= 1000) THEN
tot_len := tot_len/1000; --mostro la len in km
tlu := 'km';
END IF;
pre_string:='XMLROOT(XMLELEMENT(NAME result, XMLELEMENT(NAME route,
XMLELEMENT(NAME total_length, ''circa '||tot_len||' '||tlu||'''),
XMLELEMENT( NAME total_estimated_time, ''cerca de '||tot_time||' min''),
XMLELEMENT(NAME directions,';
steps_fragment := steps_fragment||streets[0]||'''))';
for j in 0..i LOOP
--RAISE NOTICE'geometria ------- %/',ST_AsText(geoms[j]);
steps_fragment := steps_fragment||',XMLELEMENT(NAME step,XMLELEMENT(NAME
text,'||''''||directions[j]||' '||streets[j]||' (cerca de
'||trunc(lengths[j])||' m)'||''''||'),XMLELEMENT(NAME
line,'''||ST_AsText(geoms[j])||'''))';
END LOOP;
 line_fragment:='),XMLELEMENT(NAME
complete_line,'''||ST_AsText(line)||'''))),VERSION 1.0,STANDALONE YES)';
--RAISE NOTICE'geometria -----------------------\n
--------------------------------------- \n\n %\n\n----------------------------------------',ST_AsText(line);

EXECUTE  'SELECT '||pre_string||steps_fragment||line_fragment INTO
xml_result;

RETURN xml_result;

END;

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
ALTER FUNCTION xml_directions(integer, integer, text) OWNER TO postgres;