/* Job de SQL Server Agent para carga FULL del Data Mart.
   Ejecutar una vez en msdb con permisos de SQL Server Agent.
   La carga ejecuta DELETE y reconstruye exclusivamente las tablas de REC_ECBD_Energia.
*/
USE msdb;
GO
IF EXISTS (SELECT 1 FROM msdb.dbo.sysjobs WHERE name = N'ECBD_Carga_FULL_Energia')
    EXEC msdb.dbo.sp_delete_job @job_name=N'ECBD_Carga_FULL_Energia';
GO
EXEC msdb.dbo.sp_add_job @job_name=N'ECBD_Carga_FULL_Energia',
    @enabled=1, @description=N'ETL FULL: elimina y recarga Data Mart estrella de energía.';
EXEC msdb.dbo.sp_add_jobstep @job_name=N'ECBD_Carga_FULL_Energia', @step_name=N'Ejecutar ETL FULL Python',
    @subsystem=N'CmdExec',
    @command=N'cmd /c "cd /d C:\Users\DELL\Desktop\RecurseExtracciónBD\REC_ECBD_2026_Gonzalez_Ulises && sqlcmd -S localhost -E -C -b -f 65001 -i sql\limpiar_datamart_full.sql && .venv\Scripts\python.exe -m src.ejecutar_proyecto && .venv\Scripts\python.exe -m src.etl_sqlserver --cargar"',
    @on_success_action=1, @on_fail_action=2;
EXEC msdb.dbo.sp_add_jobserver @job_name=N'ECBD_Carga_FULL_Energia';
GO
-- Ejecutar manualmente para demostrar la automatización:
-- EXEC msdb.dbo.sp_start_job @job_name=N'ECBD_Carga_FULL_Energia;
