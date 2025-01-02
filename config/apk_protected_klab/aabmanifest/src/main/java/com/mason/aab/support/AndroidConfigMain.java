package com.mason.aab.support;

import com.android.aapt.Resources;
import com.android.tools.build.bundletool.model.utils.xmlproto.*;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;

public class AndroidConfigMain {
    private static String androidNs = "http://schemas.android.com/apk/res/android";
    private enum Commands
    {
        modifyapp("modifyapp"),
        addIsolatedService("addIsolatedService");

        public String getName() {
            return name;
        }

        private String name;
        private Commands(String name) {
            this.name = name;
        }
    }

    public static void main(String[] args) {

        try {
            System.out.println("this is test call");
            if (args.length < 1)
            {
                throw new Exception("Arguments need least 2");
            }
            Commands cmd = Commands.valueOf(args[0]);
            switch (cmd)
            {
                case modifyapp:
                    String changedApplication = args[2];
                    String pbPath = args[1];
                    File file = new File(pbPath);

                    Resources.XmlNode node = Resources.XmlNode.parseFrom(new FileInputStream(file));
                    Resources.XmlNode.Builder builder =  Resources.XmlNode.newBuilder().mergeFrom(node);
//                    System.out.println(node.toString());

                    for (Resources.XmlNamespace ns : builder.getElement().getNamespaceDeclarationList())
                    {
                        if (ns.getPrefix().equals("android"))
                        {
                            androidNs = ns.getUri();
                            break;
                        }
                    }

                    for (Resources.XmlNode.Builder cnode : builder.getElementBuilder().getChildBuilderList())
                    {
                        if (cnode.hasElement() && cnode.getElementBuilder().getName().equals("application"))
                        {
                            boolean hasFindApplication = false;
                            for (Resources.XmlAttribute.Builder attr : cnode.getElementBuilder().getAttributeBuilderList())
                            {
                                if (attr.getName().equals("name"))
                                {
                                    String oriVal = attr.getValue();
                                    System.out.println(attr.getValue());
                                    hasFindApplication = true;
                                    attr.setValue(changedApplication);
                                    FileUtil.saveFile(file.getParent() + "/origin_app", oriVal);
                                    break;
                                }
                            }
                            if (!hasFindApplication)
                            {
                                System.out.println("add new attribute");
                                cnode.getElementBuilder().addAttribute(Resources.XmlAttribute.newBuilder().setName("name").setNamespaceUri(androidNs).setValue(changedApplication).setResourceId(AndroidManifest.NAME_RESOURCE_ID));
                            }

                            break;
                        }
                    }

                    FileUtil.saveFile(pbPath, builder.build().toByteArray());
                    break;
                case addIsolatedService:
                    String manifest = args[1];
                    String serviceName = args[2];
                    addIsolatedServiceInternal(manifest, serviceName);
                    break;
                default:
                    throw new Exception("no such method");
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }

    static void addIsolatedServiceInternal(String pbPath, String serviceName) throws Exception {
        File file = new File(pbPath);

        Resources.XmlNode node = Resources.XmlNode.parseFrom(new FileInputStream(file));
        Resources.XmlNode.Builder builder =  Resources.XmlNode.newBuilder().mergeFrom(node);
//                    System.out.println(node.toString());

        for (Resources.XmlNamespace ns : builder.getElement().getNamespaceDeclarationList())
        {
            if (ns.getPrefix().equals("android"))
            {
                androidNs = ns.getUri();
                break;
            }
        }
        for (Resources.XmlNode.Builder cnode : builder.getElementBuilder().getChildBuilderList())
        {
            if (cnode.hasElement() && cnode.getElementBuilder().getName().equals("application"))
            {
                //create node
                XmlProtoElement service = XmlProtoElementBuilder.create("service")
                                        .addAttribute(XmlProtoAttributeBuilder.create(androidNs, "name").setValueAsString(serviceName).setResourceId(AndroidManifest.NAME_RESOURCE_ID))
                                        .addAttribute(XmlProtoAttributeBuilder.create(androidNs, "enabled").setValueAsBoolean(true).setResourceId(AndroidManifest.ENABLED_RESOURCE_ID))
                                        .addAttribute(XmlProtoAttributeBuilder.create(androidNs, "isolatedProcess").setValueAsBoolean(true).setResourceId(AndroidManifest.ISOLATED_RESOURCE_ID)).build();

                XmlProtoNode serviceProto = XmlProtoNode.createElementNode(service);

                System.out.println(serviceProto.toString());
                cnode.getElementBuilder().addChild(serviceProto.getProto());


//                System.out.println("add service completed");
//                for (Resources.XmlNode.Builder t : cnode.getElementBuilder().getChildBuilderList())
//                {
//                    if (t.hasElement() && t.getElementBuilder().getName().equals("service"))
//                    {
//                        System.out.println("found service node:");
//                        for (Resources.XmlAttribute.Builder attr : t.getElementBuilder().getAttributeBuilderList())
//                        {
//                            System.out.println("\tattribute attr name:" + attr.getName() + " attr value:" + attr.getValue());
//                            System.out.println("\t\tresource id is :" + String.format("%x", attr.getResourceId()));
////                            if (attr.getName().equals("name"))
////                            {
////                                System.out.println("contains service node name:" + attr.getValue());
////                            }
////                            if (attr.getName().equals("isolatedProcess"))
////                            {
////                                System.out.println("contains service isolatedProcess name:" + attr.getValue());
////                            }
//                        }
//                    }
//                }
            }
        }





        FileUtil.saveFile(pbPath, builder.build().toByteArray());
    }
}
