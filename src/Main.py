import arcpy
from arcpy import env
from arcpy.sa import *

# 设置环境
arcpy.CheckOutExtension("Spatial")
env.workspace = r"D:\SSCI\StoryMAP\DMaping"  # 修改为你的工作空间路径
env.overwriteOutput = True

# 数据路径
maui_block_poly = r"DemoData\MauiLandCover.shp"  # Maui Block Polygon
maui_land_cover = r"DemoData\Block.shp"  # Maui Landcover Raster

# 将 Maui Block 转换为栅格
block_id_raster = arcpy.PolygonToRaster_conversion(maui_block_poly, "Block_ID", "Block_ID_Raster", cellsize=20)
pop_raster = arcpy.PolygonToRaster_conversion(maui_block_poly, "Total_Population", "Pop_Raster", cellsize=20)

# 计算 Tabulate Area
tab_area = TabulateArea(block_id_raster, "Value", maui_land_cover, "Value", "Tabulate_Area_Result")

# 添加和计算新字段
arcpy.AddField_management(tab_area, "Total_Pixel", "LONG")
arcpy.CalculateField_management(tab_area, "Total_Pixel", "!SUM!", "PYTHON")

arcpy.AddField_management(tab_area, "Expected_Population", "FLOAT")
exp_pop_calc = "sum([!P_{}! * {} for i in range(1, 23)])".format("{i}", "{RA[i]}")  # Pseudo-code, adjust based on actual data
arcpy.CalculateField_management(tab_area, "Expected_Population", exp_pop_calc, "PYTHON")

# 将表连接回 Block Polygon 并将字段转换为栅格
arcpy.JoinField_management(maui_block_poly, "Block_ID", tab_area, "Block_ID", ["Total_Pixel", "Expected_Population"])
total_pixel_raster = arcpy.PolygonToRaster_conversion(maui_block_poly, "Total_Pixel", "Total_Pixel_Raster", cellsize=20)
expected_pop_raster = arcpy.PolygonToRaster_conversion(maui_block_poly, "Expected_Population", "Expected_Pop_Raster", cellsize=20)

# 栅格计算器操作
population_density = Raster("RA") * Raster("Pop_Raster") * 400 / (Raster("Total_Pixel_Raster") * Raster("Expected_Pop_Raster"))
population_density.save("Population_Density_Raster")

# 清理
arcpy.CheckInExtension("Spatial")
