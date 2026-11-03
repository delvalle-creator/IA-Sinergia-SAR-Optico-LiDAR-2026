<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.44.8" styleCategories="Symbology|Fields|Forms">
  <renderer-v2 type="categorizedSymbol" attr="clase" symbollevels="0" enableorderby="0" forceraster="0">
    <categories>
      <category symbol="0" value="agua_calma" label="agua calma" render="true"/>
      <category symbol="1" value="agua_rizada" label="agua rizada" render="true"/>
      <category symbol="2" value="pajonal" label="pajonal" render="true"/>
      <category symbol="3" value="suelo_desnudo" label="suelo desnudo" render="true"/>
      <category symbol="4" value="cultivo" label="cultivo" render="true"/>
      <category symbol="5" value="monte_o_bosque" label="monte o bosque" render="true"/>
      <category symbol="6" value="urbano" label="urbano" render="true"/>
      <category symbol="7" value="estable" label="estable" render="true"/>
    </categories>
    <symbols>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="31,58,147,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="79,163,224,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="230,194,41,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="244,166,198,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="4" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="255,127,14,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="5" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="27,138,58,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="6" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="214,39,40,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="7" alpha="1" clip_to_extent="1" force_rhr="0">
        <layer class="SimpleFill" enabled="1" pass="0" locked="0">
          <Option type="Map">
            <Option type="QString" name="color" value="0,0,0,0"/>
            <Option type="QString" name="outline_color" value="127,127,127,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.7"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="no"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <fieldConfiguration>
    <field name="clase" configurationFlags="NoFlag">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option type="List" name="map">
          <Option type="Map"><Option type="QString" name="agua calma" value="agua_calma"/></Option>
          <Option type="Map"><Option type="QString" name="agua rizada" value="agua_rizada"/></Option>
          <Option type="Map"><Option type="QString" name="pajonal" value="pajonal"/></Option>
          <Option type="Map"><Option type="QString" name="suelo desnudo" value="suelo_desnudo"/></Option>
          <Option type="Map"><Option type="QString" name="cultivo" value="cultivo"/></Option>
          <Option type="Map"><Option type="QString" name="monte o bosque" value="monte_o_bosque"/></Option>
          <Option type="Map"><Option type="QString" name="urbano" value="urbano"/></Option>
          <Option type="Map"><Option type="QString" name="estable" value="estable"/></Option>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
</qgis>
